"""Pluggable proposal generators.

A `Proposer` returns a sequence of `Proposal` objects. Three built-ins:

- `MockProposer`     — fixed list of proposals supplied at construction.
                       Useful for tests and demos.
- `FileProposer`     — reads proposals from a JSON file. Useful when a
                       human or external tool drafts proposals offline.
- `AnthropicProposer` — asks a Claude model to draft proposals given a
                       summary of recent eval results and the source
                       file it's allowed to edit.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterator, Protocol

from .proposal import Proposal


class Proposer(Protocol):
    def propose(self) -> Iterator[Proposal]: ...


class MockProposer:
    def __init__(self, proposals: list[Proposal]):
        self._proposals = list(proposals)

    def propose(self) -> Iterator[Proposal]:
        for p in self._proposals:
            yield p


class FileProposer:
    """Read proposals from a JSON file shaped like:

        [
          {"label": "...", "target_path": "...", "new_content": "...",
           "rationale": "...", "proposer": "human:khaalis"},
          ...
        ]
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def propose(self) -> Iterator[Proposal]:
        for item in json.loads(self.path.read_text()):
            yield Proposal(
                label=item["label"],
                target_path=item["target_path"],
                new_content=item["new_content"],
                rationale=item.get("rationale", ""),
                proposer=item.get("proposer", "file"),
            )


class AnthropicProposer:
    """Generate proposals using a Claude model.

    The model receives:
      - The current source of the target file.
      - A summary of recent eval-suite outcomes.
      - The system prompt below.

    It returns one Proposal per call. The caller is expected to invoke
    multiple times to explore different ideas.
    """

    SYSTEM = (
        "You are an engineer improving the wofo investment-research agent. "
        "Propose narrow, well-justified changes to a single file at a time. "
        "Each change must be small enough that a human reviewer can audit it "
        "in under five minutes. Do NOT add features beyond what is needed. "
        "Do NOT introduce new dependencies. Output a JSON object with "
        "fields: label, target_path, new_content, rationale."
    )

    def __init__(
        self,
        target_path: str,
        eval_summary: str,
        *,
        model: str = "claude-opus-4-7",
        max_tokens: int = 4096,
    ):
        self.target_path = target_path
        self.eval_summary = eval_summary
        self.model = model
        self.max_tokens = max_tokens

    def propose(self) -> Iterator[Proposal]:
        try:
            import anthropic  # type: ignore
        except ImportError:
            raise RuntimeError("install `anthropic` to use AnthropicProposer")
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        client = anthropic.Anthropic()
        repo_root = Path(__file__).resolve().parents[2]
        current = (repo_root / self.target_path).read_text()

        user = (
            f"Target file: {self.target_path}\n\n"
            "<current_source>\n"
            f"{current}\n"
            "</current_source>\n\n"
            "<eval_summary>\n"
            f"{self.eval_summary}\n"
            "</eval_summary>\n\n"
            "Propose ONE change to this file. Output JSON only."
        )
        resp = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        txt = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        try:
            payload = _extract_json(txt)
        except ValueError as e:
            raise RuntimeError(f"AnthropicProposer: model did not return JSON: {e}") from e
        yield Proposal(
            label=payload.get("label", "anthropic"),
            target_path=payload.get("target_path", self.target_path),
            new_content=payload["new_content"],
            rationale=payload.get("rationale", ""),
            proposer=f"anthropic:{self.model}",
        )


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        # Strip code-fence wrapper.
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                return json.loads(text[start : i + 1])
    raise ValueError("no JSON object found")
