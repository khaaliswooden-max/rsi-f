"""CLI for the 13F pipeline.

Examples:
    # Pull all filings for Situational Awareness LP into wofo/data/13f/raw/
    python -m wofo.thirteenf.cli pull --cik 0002045724

    # Parse the local raw/ tree and write processed/ JSON + analysis
    python -m wofo.thirteenf.cli analyze
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .fetch import list_filings, fetch_filing
from .parse import parse_infotable, parse_primary_doc
from .analyze import build_panel, qoq_changes, concentration

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW = REPO_ROOT / "wofo" / "data" / "13f" / "raw"
DEFAULT_PROCESSED = REPO_ROOT / "wofo" / "data" / "13f" / "processed"


def _cmd_pull(args: argparse.Namespace) -> None:
    raw = Path(args.raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    refs = list_filings(args.cik)
    print(f"Found {len(refs)} 13F filings for CIK {args.cik}")
    for ref in refs:
        print(f"  {ref.period_ending}  {ref.form}  {ref.accession}")
        fetch_filing(ref, raw)
    print(f"Wrote raw filings to {raw}")


def _cmd_analyze(args: argparse.Namespace) -> None:
    raw = Path(args.raw_dir)
    out = Path(args.processed_dir)
    out.mkdir(parents=True, exist_ok=True)

    quarters = sorted(p for p in raw.iterdir() if p.is_dir())
    pairs = []
    for q in quarters:
        meta = parse_primary_doc(q / "primary_doc.xml")
        holdings = parse_infotable(q / "infotable.xml")
        pairs.append((meta, holdings))
        # Per-quarter normalized JSON.
        (out / f"{q.name}.json").write_text(
            json.dumps(
                {
                    "meta": meta.__dict__,
                    "holdings": [h.to_dict() for h in holdings],
                },
                indent=2,
            )
        )

    panel = build_panel(pairs)
    deltas = qoq_changes(panel)
    conc = concentration(panel)

    # Convert tuple keys for JSON.
    rows_serializable = {f"{p}|{c}": v for (p, c), v in panel["rows"].items()}
    (out / "panel.json").write_text(
        json.dumps(
            {
                "periods": panel["periods"],
                "issuers": panel["issuers"],
                "rows": rows_serializable,
                "totals": panel["totals"],
            },
            indent=2,
        )
    )
    (out / "qoq_changes.json").write_text(json.dumps(deltas, indent=2))
    (out / "concentration.json").write_text(json.dumps(conc, indent=2))

    _print_summary(pairs, panel, deltas, conc)


def _print_summary(pairs, panel, deltas, conc) -> None:
    print()
    print(f"Manager: {pairs[-1][0].manager_name}  (CIK {pairs[-1][0].cik})")
    print(f"Quarters: {', '.join(panel['periods'])}")
    print()
    print(f"{'Period':<12}{'Positions':>10}{'Total $M':>12}{'Top5':>8}{'Top10':>8}{'HHI':>8}")
    for p in panel["periods"]:
        c = conc[p]
        print(
            f"{p:<12}{c['n_positions']:>10}"
            f"{c['total_value_usd']/1e6:>12,.1f}"
            f"{c['top_5_share']*100:>7.1f}%"
            f"{c['top_10_share']*100:>7.1f}%"
            f"{c['hhi']:>8.3f}"
        )
    print()
    latest = panel["periods"][-1]
    latest_actions = [d for d in deltas if d["period"] == latest]
    by_action = {}
    for d in latest_actions:
        by_action.setdefault(d["action"], []).append(d)
    print(f"Latest quarter ({latest}) activity:")
    for a in ("NEW", "EXIT", "ADD", "TRIM", "HOLD"):
        rows = by_action.get(a, [])
        rows.sort(key=lambda r: abs(r["value_delta_usd"]), reverse=True)
        print(f"  {a:<5} {len(rows):>3}  top: " + ", ".join(
            f"{r['issuer']} ({r['value_delta_usd']/1e6:+.1f}M)" for r in rows[:5]
        ))


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="wofo.thirteenf")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("pull", help="Download 13F filings from EDGAR")
    pl.add_argument("--cik", required=True, help="10-digit or shorter CIK")
    pl.add_argument("--raw-dir", default=str(DEFAULT_RAW))
    pl.set_defaults(func=_cmd_pull)

    an = sub.add_parser("analyze", help="Parse local raw/ filings into processed/")
    an.add_argument("--raw-dir", default=str(DEFAULT_RAW))
    an.add_argument("--processed-dir", default=str(DEFAULT_PROCESSED))
    an.set_defaults(func=_cmd_analyze)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
