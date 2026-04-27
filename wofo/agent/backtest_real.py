"""Real-price backtest of the follow-the-filer strategy on cached Yahoo data.

Run:
    python -m wofo.agent.backtest_real

Cache directory `wofo/data/prices/` is checked in for reproducibility
across machines / CI. Re-pull by deleting it and running this script
again (Yahoo v8, free).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from wofo.thirteenf import parse_infotable, parse_primary_doc, build_panel
from wofo.research import IssuerOverride, follow_the_filer
from wofo.research.follow_the_filer import load_filing_refs
from wofo.backtest import run_backtest, summary
from wofo.prices.yahoo import YahooPriceSource
from wofo.prices.cache import CachingPriceSource

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "wofo" / "data" / "13f" / "raw"
PRICES_DIR = REPO / "wofo" / "data" / "prices"
REPORT = REPO / "wofo" / "data" / "13f" / "processed" / "BACKTEST_REAL.md"


# Issuer -> ticker overrides. Keep in one place so demos and tests share.
SA_LP_OVERRIDES = IssuerOverride(by_issuer={
    "COREWEAVE INC": "CRWV",
    "BLOOM ENERGY CORP": "BE",
    "INTEL CORP": "INTC",
    "LUMENTUM HLDGS INC": "LITE",
    "CORE SCIENTIFIC INC NEW": "CORZ",
    "IREN LIMITED": "IREN",
    "APPLIED DIGITAL CORP": "APLD",
    "SANDISK CORP": "SNDK",
    "EQT CORP": "EQT",
    "CIPHER MINING INC": "CIFR",
    "COHERENT CORP": "COHR",
    "CONSTELLATION ENERGY CORP": "CEG",
    "MARVELL TECHNOLOGY INC": "MRVL",
    "MODINE MFG CO": "MOD",
    "ANTERIX INC": "ATEX",
    "VISTRA CORP": "VST",
    "NVIDIA CORPORATION": "NVDA",
    "BROADCOM INC": "AVGO",
    "TAIWAN SEMICONDUCTOR MFG LTD": "TSM",
    "MICRON TECHNOLOGY INC": "MU",
    "WESTERN DIGITAL CORP": "WDC",
    "SEAGATE TECHNOLOGY HLDNGS PL": "STX",
    "GALAXY DIGITAL INC.": "GLXY",
    "CLEANSPARK INC": "CLSK",
    "BITFARMS LTD": "BITF",
    "LIBERTY ENERGY INC": "LBRT",
    "INFOSYS LTD": "INFY",
    "PROPETRO HLDG CORP": "PUMP",
    "BABCOCK & WILCOX ENTERPRISES": "BW",
    "POWER SOLUTIONS INTL INC": "PSIX",
    "WHITEFIBER INC": "WYFI",
    "KILROY RLTY CORP": "KRC",
})


def main() -> None:
    pairs = []
    for q in sorted(p for p in RAW.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    refs = load_filing_refs(RAW)

    cusip_to_ticker = {c: SA_LP_OVERRIDES.by_issuer.get(n) for c, n in panel["issuers"].items()}
    tw = follow_the_filer(
        panel,
        filing_refs=refs,
        cusip_to_ticker=cusip_to_ticker,
        manager_cik="0002045724",
        manager_name="Situational Awareness LP",
        run_id="backtest_real",
    )

    src = CachingPriceSource(YahooPriceSource(), PRICES_DIR)
    # Tighter threshold = more rebalances + more cost. 250bps lets the book
    # drift naturally between filings while still tracking new snapshots.
    res = run_backtest(
        tw,
        src,
        start_cash=1_000_000.0,
        end_date=date(2026, 4, 26),
        rebalance_threshold_bps=250.0,
    )
    s = summary(res.dates, res.nav)

    # Benchmark: SPY held over the same period.
    spy_bars = src.daily("SPY", res.dates[0], res.dates[-1])
    spy_close = {b.d: b.close for b in spy_bars}
    spy_dates = sorted(d for d in res.dates if d in spy_close)
    if spy_dates:
        base = spy_close[spy_dates[0]]
        spy_nav = [res.nav[0] * spy_close[d] / base for d in spy_dates]
        spy_summary = summary(spy_dates, spy_nav)
    else:
        spy_summary = None

    out = {
        "strategy": "follow Situational Awareness LP",
        "manager_cik": tw.manager_cik,
        "snapshots": len(tw.snapshots),
        "start_cash": 1_000_000.0,
        "summary": s,
        "benchmark_spy": spy_summary,
        "rebalance_dates": [d.isoformat() for d in res.rebalance_dates],
        "skipped_tickers": {d.isoformat(): t for d, t in res.skipped_tickers.items()},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.with_suffix(".json").write_text(json.dumps(out, indent=2, default=str))

    md = _format_report(out, res, tw)
    REPORT.write_text(md)
    print(md)


def _format_report(out: dict, res, tw) -> str:
    s = out["summary"]
    bench = out["benchmark_spy"]
    lines = [
        "# Real-price backtest — follow Situational Awareness LP",
        "",
        f"Manager CIK: `{out['manager_cik']}`",
        f"Snapshots: {out['snapshots']}",
        f"Start cash: ${out['start_cash']:,.0f}",
        f"Window: {s['start_date']} → {s['end_date']} ({s['n_days']} trading days)",
        "",
        "## Strategy vs SPY",
        "",
        "| Metric | Strategy | SPY (buy & hold) |",
        "|---|---:|---:|",
        f"| End NAV | ${s['end_nav']:,.0f} | ${bench['end_nav']:,.0f} |" if bench else f"| End NAV | ${s['end_nav']:,.0f} | n/a |",
        f"| Total return | {s['total_return']:.1%} | {bench['total_return']:.1%} |" if bench else f"| Total return | {s['total_return']:.1%} | n/a |",
        f"| CAGR | {s['cagr']:.1%} | {bench['cagr']:.1%} |" if bench else f"| CAGR | {s['cagr']:.1%} | n/a |",
        f"| Sharpe | {s['sharpe']:.2f} | {bench['sharpe']:.2f} |" if bench else f"| Sharpe | {s['sharpe']:.2f} | n/a |",
        f"| Max drawdown | {s['max_drawdown']:.1%} | {bench['max_drawdown']:.1%} |" if bench else f"| Max drawdown | {s['max_drawdown']:.1%} | n/a |",
        "",
        f"## Rebalances ({len(res.rebalance_dates)} total)",
        "",
        "Snapshot effective dates (these are forced rebalances on each new filing):",
        "",
    ]
    snapshot_dates = {s.effective_date for s in tw.snapshots}
    for d in res.rebalance_dates:
        if d in snapshot_dates or any(abs((d - sd).days) <= 3 for sd in snapshot_dates):
            lines.append(f"- {d.isoformat()} (snapshot)")
    drift_count = len([d for d in res.rebalance_dates if d not in snapshot_dates and not any(abs((d - sd).days) <= 3 for sd in snapshot_dates)])
    lines.append(f"")
    lines.append(f"Plus {drift_count} drift-triggered rebalances (threshold 250 bps).")
    if res.skipped_tickers:
        lines += ["", "## Tickers skipped (no price coverage on snapshot date)", ""]
        for d in sorted(res.skipped_tickers):
            lines.append(f"- {d.isoformat()}: {', '.join(res.skipped_tickers[d])}")
    lines += [
        "",
        "## Caveats",
        "",
        "- 13F is long-only and stale by ~45 days (we use file_date as effective).",
        "- Yahoo v8 chart data is unofficial; corporate-action handling is not institutional-grade.",
        "- Some SA LP names (CRWV, SNDK, GLXY, WYFI) listed mid-window; the backtester held cash for those weights until they were tradable.",
        "- Sharpe assumes 0 risk-free rate; flip the rf_annual arg for a different baseline.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
