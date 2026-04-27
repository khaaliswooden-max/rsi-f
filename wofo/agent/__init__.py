"""wofo agent — Phase 1 (research only).

This module defines the *tools* the wofo agent is allowed to call and
the orchestration loop that drives it. By construction, Phase 1
exposes only **read-only research tools** — no execution, no order
entry, no broker connectivity. Phase 2 / 3 will live in separate
modules and require a deliberate code change (and counsel sign-off)
to enable.

The agent uses the Anthropic Python SDK if available; if it is not
installed, the tools can still be invoked directly from Python.
"""
from .tools import TOOLS, dispatch_tool, ToolResult
from .runner import run_research_loop

__all__ = ["TOOLS", "dispatch_tool", "ToolResult", "run_research_loop"]
