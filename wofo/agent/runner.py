"""Research-loop runner.

Drives a Claude model through a tool-use loop using only the read-only
research tools defined in `wofo.agent.tools`. Requires the `anthropic`
SDK at runtime; if it is not installed the module still imports so the
tools can be used without a model.
"""
from __future__ import annotations

import os
from typing import Any

from .tools import TOOLS, dispatch_tool


SYSTEM_PROMPT = """You are wofo, the Wooden Family Office research agent.

You operate in Phase 1 — research only. You have NO ability to place
orders, transfer funds, or modify any account. You may only call the
read-only research tools provided.

Your job is to produce well-sourced, dated research notes:
- Cite filings by accession number when relevant.
- Be explicit about staleness (13F is delayed by up to 45 days).
- When you don't know, say so. Never fabricate tickers or numbers.
- Distinguish "the manager held X" (fact) from "X is a good buy"
  (opinion that needs justification).

When you finish, return a research note in markdown.
""".strip()


def run_research_loop(
    user_prompt: str,
    *,
    model: str = "claude-opus-4-7",
    max_iterations: int = 8,
    max_tokens: int = 4096,
) -> dict:
    """Run a single research-task loop and return the final transcript.

    The function returns a dict with `final_text`, `messages` (full
    transcript), and `tool_calls` (audit log). It does not stream.
    """
    try:
        import anthropic  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "anthropic SDK is required to run the agent loop; "
            "`pip install anthropic` and set ANTHROPIC_API_KEY."
        ) from e

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")

    client = anthropic.Anthropic()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_prompt}]
    tool_calls: list[dict[str, Any]] = []

    for _ in range(max_iterations):
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        # Append assistant turn.
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
            return {"final_text": text, "messages": messages, "tool_calls": tool_calls}

        # Run every tool call in the assistant turn.
        tool_results: list[dict[str, Any]] = []
        for block in resp.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            tr = dispatch_tool(block.name, block.input)
            tool_calls.append(
                {"name": block.name, "input": block.input, "ok": tr.ok, "error": tr.error}
            )
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": tr.to_message()["content"],
                    "is_error": tr.to_message()["is_error"],
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return {
        "final_text": "(max iterations reached)",
        "messages": messages,
        "tool_calls": tool_calls,
    }
