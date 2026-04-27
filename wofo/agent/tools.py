"""Tools the wofo Phase-1 agent can call.

Each tool is a pure-Python function with a JSON-Schema-style signature.
The signatures double as the Anthropic tool-use definitions when the
agent is wired to Claude.

**No tool in this module places orders, transfers funds, or modifies
any account.** Adding such a tool requires:
1. Counsel sign-off (see docs/family-office-counsel-packet.md).
2. Phase-2 promotion in docs/wofo-architecture.md.
3. Hard guardrails (per-trade caps, daily caps, kill switch).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from wofo.thirteenf import parse_infotable, parse_primary_doc, build_panel, qoq_changes, concentration


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "wofo" / "data" / "13f" / "raw"


@dataclass
class ToolResult:
    name: str
    ok: bool
    content: Any
    error: str | None = None

    def to_message(self) -> dict:
        return {
            "type": "tool_result",
            "content": json.dumps(self.content) if self.ok else self.error or "error",
            "is_error": not self.ok,
        }


# --- Tool implementations ---------------------------------------------------


def t_list_local_filings(manager_dir: str = "") -> dict:
    """List 13F filing periods we have on disk."""
    base = RAW_DIR if not manager_dir else (REPO_ROOT / manager_dir)
    if not base.exists():
        return {"periods": [], "base": str(base)}
    periods = sorted(p.name for p in base.iterdir() if p.is_dir())
    return {"periods": periods, "base": str(base)}


def t_summarize_panel() -> dict:
    """Build a panel from local 13F filings and return a summary."""
    pairs = []
    for q in sorted(p for p in RAW_DIR.iterdir() if p.is_dir()):
        meta = parse_primary_doc(q / "primary_doc.xml")
        rows = parse_infotable(q / "infotable.xml")
        pairs.append((meta, rows))
    panel = build_panel(pairs)
    conc = concentration(panel)
    return {
        "manager": pairs[-1][0].manager_name if pairs else None,
        "cik": pairs[-1][0].cik if pairs else None,
        "periods": panel["periods"],
        "concentration": conc,
        "totals": panel["totals"],
    }


def t_top_holdings(period: str, n: int = 10) -> dict:
    """Top N holdings for a given period."""
    pairs = []
    for q in sorted(p for p in RAW_DIR.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    if period not in panel["periods"]:
        raise ValueError(f"unknown period {period}; have {panel['periods']}")
    rows = [
        {"cusip": c, "issuer": panel["issuers"].get(c, ""), "value_usd": r["value_usd"], "shares": r["shares"]}
        for (p, c), r in panel["rows"].items() if p == period
    ]
    rows.sort(key=lambda r: r["value_usd"], reverse=True)
    return {"period": period, "holdings": rows[:n]}


def t_qoq_activity(period: str) -> dict:
    """Quarter-over-quarter activity (NEW/EXIT/ADD/TRIM/HOLD) for a period."""
    pairs = []
    for q in sorted(p for p in RAW_DIR.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    deltas = qoq_changes(panel)
    return {"period": period, "rows": [d for d in deltas if d["period"] == period]}


# --- Registry ---------------------------------------------------------------


def _schema(name: str, description: str, props: dict, required: list[str]) -> dict:
    return {
        "name": name,
        "description": description,
        "input_schema": {"type": "object", "properties": props, "required": required},
    }


TOOLS: list[dict] = [
    _schema(
        "list_local_filings",
        "List 13F filing periods available on local disk.",
        {"manager_dir": {"type": "string", "description": "optional path; default = the SA LP raw dir"}},
        [],
    ),
    _schema(
        "summarize_panel",
        "Summarize the panel of 13F filings on disk: manager, periods, totals, concentration.",
        {},
        [],
    ),
    _schema(
        "top_holdings",
        "Return the top-N holdings (by reported value) for a given period (YYYY-MM-DD).",
        {
            "period": {"type": "string", "description": "Period of report, e.g. 2025-12-31"},
            "n": {"type": "integer", "description": "How many top holdings to return", "default": 10},
        },
        ["period"],
    ),
    _schema(
        "qoq_activity",
        "Quarter-over-quarter activity (NEW/EXIT/ADD/TRIM/HOLD) for a period.",
        {"period": {"type": "string", "description": "Period of report, e.g. 2025-12-31"}},
        ["period"],
    ),
]


_DISPATCH: dict[str, Callable[..., dict]] = {
    "list_local_filings": t_list_local_filings,
    "summarize_panel": t_summarize_panel,
    "top_holdings": t_top_holdings,
    "qoq_activity": t_qoq_activity,
}


def dispatch_tool(name: str, args: dict | None) -> ToolResult:
    fn = _DISPATCH.get(name)
    if fn is None:
        return ToolResult(name=name, ok=False, content=None, error=f"unknown tool: {name}")
    try:
        result = fn(**(args or {}))
        return ToolResult(name=name, ok=True, content=result)
    except Exception as e:  # surface errors to the model so it can recover
        return ToolResult(name=name, ok=False, content=None, error=f"{type(e).__name__}: {e}")
