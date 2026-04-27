"""Analyze a panel of 13F holdings across quarters.

Inputs are the dataclasses produced by `parse.py`. Outputs are plain dicts /
lists so the module has zero hard dependencies (no pandas required).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .parse import Holding, FilingMeta


def build_panel(filings: Iterable[tuple[FilingMeta, list[Holding]]]) -> dict:
    """Build a panel keyed by (period_iso, cusip).

    Returns:
      {
        "periods": [iso, ...],          # sorted ascending
        "issuers": {cusip: name},       # latest known name per cusip
        "rows": {(period, cusip): {...}},
        "totals": {period: {"value_usd": int, "n_positions": int}},
      }
    """
    periods: list[str] = []
    issuers: dict[str, str] = {}
    rows: dict[tuple[str, str], dict] = {}
    totals: dict[str, dict] = {}

    for meta, holdings in filings:
        p = meta.period_iso
        periods.append(p)
        agg_value = 0
        # Some funds report multiple lines per CUSIP (e.g. SH + put/call). Aggregate by cusip.
        bucket: dict[str, dict] = defaultdict(
            lambda: {"value_usd": 0, "shares": 0, "lines": 0}
        )
        for h in holdings:
            issuers[h.cusip] = h.name_of_issuer
            b = bucket[h.cusip]
            b["value_usd"] += h.value_usd
            # Only count SH lines toward share count; PRN is principal, not shares.
            if h.sh_or_prn == "SH" and not h.put_call:
                b["shares"] += h.shares_or_principal
            b["lines"] += 1
            b["name"] = h.name_of_issuer
            agg_value += h.value_usd

        for cusip, b in bucket.items():
            rows[(p, cusip)] = b
        totals[p] = {"value_usd": agg_value, "n_positions": len(bucket)}

    periods = sorted(set(periods))
    return {"periods": periods, "issuers": issuers, "rows": rows, "totals": totals}


def qoq_changes(panel: dict) -> list[dict]:
    """Compute quarter-over-quarter deltas.

    For each consecutive pair of periods, classify each cusip as:
      NEW       — present in current, absent in prior
      EXIT      — present in prior, absent in current
      ADD       — share count up >5% (or value up >5% for non-SH)
      TRIM      — share count down >5%
      HOLD      — within +/-5%

    Returns one row per (period, cusip).
    """
    out: list[dict] = []
    rows = panel["rows"]
    issuers = panel["issuers"]
    periods = panel["periods"]
    for i, cur in enumerate(periods):
        prev = periods[i - 1] if i > 0 else None
        cur_cusips = {c for (p, c) in rows if p == cur}
        prev_cusips = {c for (p, c) in rows if p == prev} if prev else set()
        union = cur_cusips | prev_cusips
        for cusip in sorted(union):
            cur_row = rows.get((cur, cusip))
            prev_row = rows.get((prev, cusip)) if prev else None
            cur_val = cur_row["value_usd"] if cur_row else 0
            prev_val = prev_row["value_usd"] if prev_row else 0
            cur_shrs = cur_row["shares"] if cur_row else 0
            prev_shrs = prev_row["shares"] if prev_row else 0

            if prev is None:
                action = "INITIAL"
            elif cur_row and not prev_row:
                action = "NEW"
            elif prev_row and not cur_row:
                action = "EXIT"
            else:
                # Prefer share delta when both sides have SH counts; else value delta.
                if cur_shrs and prev_shrs:
                    pct = (cur_shrs - prev_shrs) / prev_shrs
                else:
                    pct = (cur_val - prev_val) / prev_val if prev_val else 0
                if pct > 0.05:
                    action = "ADD"
                elif pct < -0.05:
                    action = "TRIM"
                else:
                    action = "HOLD"

            out.append(
                {
                    "period": cur,
                    "prev_period": prev,
                    "cusip": cusip,
                    "issuer": issuers.get(cusip, ""),
                    "action": action,
                    "value_usd": cur_val,
                    "prev_value_usd": prev_val,
                    "shares": cur_shrs,
                    "prev_shares": prev_shrs,
                    "value_delta_usd": cur_val - prev_val,
                    "share_delta": cur_shrs - prev_shrs,
                }
            )
    return out


def concentration(panel: dict) -> dict[str, dict]:
    """Per-period concentration metrics: top-N share, HHI, n_positions."""
    out: dict[str, dict] = {}
    for period in panel["periods"]:
        period_rows = [
            (cusip, r) for (p, cusip), r in panel["rows"].items() if p == period
        ]
        total = sum(r["value_usd"] for _, r in period_rows) or 1
        weights = sorted((r["value_usd"] / total for _, r in period_rows), reverse=True)
        hhi = sum(w * w for w in weights)  # Herfindahl on portfolio weights
        out[period] = {
            "n_positions": len(period_rows),
            "total_value_usd": sum(r["value_usd"] for _, r in period_rows),
            "top_5_share": sum(weights[:5]),
            "top_10_share": sum(weights[:10]),
            "hhi": hhi,
            "effective_n": (1 / hhi) if hhi else 0,
        }
    return out
