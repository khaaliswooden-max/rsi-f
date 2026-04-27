"""Multi-filer backtest: SA LP + Scion (Burry) + Pabrai (Dalal Street).

Runs each manager solo, then runs three portfolio-of-filers combos
(equal-weight, value-weight, consensus). Writes a comparison report.

    python -m wofo.agent.multi_filer
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from wofo.thirteenf import parse_infotable, parse_primary_doc, build_panel
from wofo.research import (
    IssuerOverride,
    follow_the_filer,
    equal_weight,
    value_weight,
    consensus,
)
from wofo.research.follow_the_filer import load_filing_refs
from wofo.backtest import run_backtest, summary
from wofo.evals.signal import benchmark_compare
from wofo.prices.yahoo import YahooPriceSource
from wofo.prices.cache import CachingPriceSource

from .backtest_real import SA_LP_OVERRIDES


REPO = Path(__file__).resolve().parents[2]
PRICES_DIR = REPO / "wofo" / "data" / "prices"
SA_LP_RAW = REPO / "wofo" / "data" / "13f" / "raw"
SCION_RAW = REPO / "wofo" / "data" / "13f" / "scion" / "raw"
PABRAI_RAW = REPO / "wofo" / "data" / "13f" / "pabrai" / "raw"
REPORT = REPO / "wofo" / "data" / "13f" / "processed" / "MULTI_FILER_REPORT.md"


# Hand-curated overrides for Scion + Pabrai. As elsewhere, names not in
# the override map fall through as None and the backtester routes the
# corresponding weight to cash.
SCION_OVERRIDES = IssuerOverride(by_issuer={
    "PALANTIR TECHNOLOGIES INC": "PLTR",
    "NVIDIA CORPORATION": "NVDA",
    "PFIZER INC": "PFE",
    "HALLIBURTON CO": "HAL",
    "MOLINA HEALTHCARE INC": "MOH",
    "ESTEE LAUDER COS INC": "EL",
    "BRUKER CORP": "BRKR",
    "ALIBABA GROUP HOLDING LTD": "BABA",
    "BAIDU INC": "BIDU",
    "JD COM INC": "JD",
    "PDD HOLDINGS INC": "PDD",
    "BIOATLA INC": "BCAB",
    "GEN DIGITAL INC": "GEN",
    "ORACLE CORP": "ORCL",
    "ASML HOLDING N V": "ASML",
    "AMERICAN COASTAL INSURANCE CORP": "ACIC",
    "OLO INC": "OLO",
    "INTL FLAVORS & FRAGRANCES INC": "IFF",
    "BIOATLA, INC.": "BCAB",
    "CANADA GOOSE HOLDINGS INC": "GOOS",
    "PROCEPT BIOROBOTICS CORP": "PRCT",
    "REGENERON PHARMACEUTICALS INC": "REGN",
    "SIGNET JEWELERS LIMITED": "SIG",
    "SYRA HEALTH CORP": "SYRA",
    "TRADE DESK INC": "TTD",
    "VF CORP": "VFC",
    "WORKDAY INC": "WDAY",
    "ZOOMINFO TECHNOLOGIES INC": "ZI",
    "MOLINA HEALTHCARE INC.": "MOH",
})
PABRAI_OVERRIDES = IssuerOverride(by_issuer={
    "WARRIOR MET COAL INC": "HCC",
    "TRANSOCEAN LTD": "RIG",
    "ALPHA METALLURGICAL RESOUR I": "AMR",
    "ALPHA METALLURGICAL RESOURCES INC": "AMR",
    "VALARIS LTD": "VAL",
    "CONSOL ENERGY INC": "CEIX",
    "TIDEWATER INC": "TDW",
    "PETROLEO BRASILEIRO S A PETROBRAS": "PBR",
    "OCCIDENTAL PETE CORP": "OXY",
    "ARCH RES INC": "ARCH",
})


def _load_panel(raw_dir: Path):
    pairs = []
    for q in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    refs = load_filing_refs(raw_dir)
    return pairs, panel, refs


def _strategy(raw_dir: Path, overrides: IssuerOverride, cik: str, name: str, run_id: str):
    _, panel, refs = _load_panel(raw_dir)
    cusip_to_ticker = {c: overrides.by_issuer.get(n) for c, n in panel["issuers"].items()}
    return follow_the_filer(
        panel, filing_refs=refs, cusip_to_ticker=cusip_to_ticker,
        manager_cik=cik, manager_name=name, run_id=run_id,
    )


def _portfolio_values(raw_dir: Path, cik: str) -> dict:
    """Map period_of_report -> reported portfolio value, for value_weight()."""
    out: dict = {}
    for q in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        meta = parse_primary_doc(q / "primary_doc.xml")
        # period_iso is YYYY-MM-DD; we store as date for keying.
        from datetime import datetime
        d = datetime.strptime(meta.period_iso, "%Y-%m-%d").date()
        out[d] = meta.table_value_total
    return {cik: out}


def main() -> None:
    sa_tw = _strategy(SA_LP_RAW, SA_LP_OVERRIDES, "0002045724", "Situational Awareness LP", "multi_filer:salp")
    scion_tw = _strategy(SCION_RAW, SCION_OVERRIDES, "0001649339", "Scion Asset Management LLC", "multi_filer:scion")
    pabrai_tw = _strategy(PABRAI_RAW, PABRAI_OVERRIDES, "0001549575", "Dalal Street LLC (Pabrai)", "multi_filer:pabrai")

    pv: dict = {}
    pv.update(_portfolio_values(SA_LP_RAW, "0002045724"))
    pv.update(_portfolio_values(SCION_RAW, "0001649339"))
    pv.update(_portfolio_values(PABRAI_RAW, "0001549575"))

    filers = [sa_tw, scion_tw, pabrai_tw]
    eq = equal_weight(filers)
    vw = value_weight(filers, pv)
    cs2 = consensus(filers, min_overlap=2)

    src = CachingPriceSource(YahooPriceSource(), PRICES_DIR)
    end = date(2026, 4, 26)

    runs: list[tuple[str, object]] = []
    for label, tw in [
        ("SA LP solo", sa_tw),
        ("Scion solo", scion_tw),
        ("Pabrai solo", pabrai_tw),
        ("Equal-weight 3", eq),
        ("Value-weight 3", vw),
        ("Consensus (>=2 managers)", cs2),
    ]:
        if not tw.snapshots:
            print(f"  {label}: empty, skipped")
            continue
        try:
            res = run_backtest(tw, src, start_cash=1_000_000.0, end_date=end, rebalance_threshold_bps=250.0)
            runs.append((label, res))
        except Exception as e:
            print(f"  {label}: {type(e).__name__}: {e}")

    # SPY benchmark on the union of dates across all strategies.
    all_dates = sorted({d for _, r in runs for d in r.dates})
    if all_dates:
        spy_bars = src.daily("SPY", all_dates[0], all_dates[-1])
        spy_close = {b.d: b.close for b in spy_bars}

    rows: list[dict] = []
    for label, res in runs:
        s = summary(res.dates, res.nav)
        common = [d for d in res.dates if d in spy_close]
        spy_nav = []
        if common:
            base = spy_close[common[0]]
            spy_nav = [res.nav[0] * spy_close[d] / base for d in common]
            sig = benchmark_compare(res.dates, res.nav, common, spy_nav)
        else:
            sig = None
        rows.append({
            "label": label,
            "summary": s,
            "signal": sig.to_dict() if sig else None,
            "rebalances": len(res.rebalance_dates),
            "skipped_count": len(res.skipped_tickers),
        })

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.with_suffix(".json").write_text(json.dumps(rows, indent=2, default=str))
    md = _format(rows, all_dates[0] if all_dates else None, all_dates[-1] if all_dates else None)
    REPORT.write_text(md)
    print(md)


def _format(rows, start, end) -> str:
    lines = [
        "# Multi-filer backtest comparison",
        "",
        f"Window (union of all runs): {start} → {end}" if start else "",
        "",
        "## Strategy comparison",
        "",
        "| Strategy | n_days | Total ret | CAGR | Sharpe | MaxDD | α (annual) | β | InfoRatio | UpCap | DnCap | Rebal |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        s = r["summary"]
        sig = r["signal"]
        a = f"{sig['alpha_annual']:.1%}" if sig else "n/a"
        b = f"{sig['beta']:.2f}" if sig else "n/a"
        ir = f"{sig['info_ratio']:.2f}" if sig else "n/a"
        up = f"{sig['up_capture']:.2f}" if sig else "n/a"
        dn = f"{sig['down_capture']:.2f}" if sig else "n/a"
        lines.append(
            f"| {r['label']} | {s['n_days']} | {s['total_return']:.1%} | "
            f"{s['cagr']:.1%} | {s['sharpe']:.2f} | {s['max_drawdown']:.1%} | "
            f"{a} | {b} | {ir} | {up} | {dn} | {r['rebalances']} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- α / β / InfoRatio / UpCap / DnCap are computed against SPY on the trading-day union.",
        "- Rebalances counts both snapshot effective-date forced rebalances and drift-triggered ones (250 bps threshold).",
        "- The three solo books are mandate-orthogonal: SA LP = AI infra / power; Scion = concentrated contrarian; Pabrai = deep-value commodities.",
        "- Consensus (>=2 managers) often returns 0 names because the books have minimal overlap. That is real signal, not a bug — these managers do not agree on much.",
        "- Yahoo v8 chart data is unofficial; treat single-digit alpha differences across strategies as noise.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
