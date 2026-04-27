"""N-filer multi-manager backtest with factor decomposition.

Generalization of `multi_filer.py` to an arbitrary roster of 13F filers.
Adds Fama-French-style factor decomposition (ETF-proxy factors) on top
of the SPY-benchmark comparison.

    python -m wofo.agent.multi_filer_n
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Sequence

from wofo.thirteenf import parse_primary_doc, parse_infotable, build_panel
from wofo.research import (
    COMMON_OVERRIDES,
    follow_the_filer,
    equal_weight,
    value_weight,
    consensus,
)
from wofo.research.follow_the_filer import load_filing_refs
from wofo.research.issuer_map import resolve_tickers
from wofo.backtest import run_backtest, summary
from wofo.evals.signal import benchmark_compare, factor_decompose
from wofo.factors import EtfProxyFactors
from wofo.prices.yahoo import YahooPriceSource
from wofo.prices.cache import CachingPriceSource


REPO = Path(__file__).resolve().parents[2]
PRICES_DIR = REPO / "wofo" / "data" / "prices"
F13_DIR = REPO / "wofo" / "data" / "13f"
SEC_TICKERS_CACHE = REPO / "wofo" / "data" / "sec_company_tickers.json"
REPORT = REPO / "wofo" / "data" / "13f" / "processed" / "MULTI_FILER_N_REPORT.md"


@dataclass(frozen=True)
class Filer:
    slug: str
    cik: str
    name: str
    raw_dir: Path

    @classmethod
    def make(cls, slug: str, cik: str, name: str) -> "Filer":
        raw = F13_DIR / "raw" if slug == "salp" else F13_DIR / slug / "raw"
        return cls(slug=slug, cik=cik, name=name, raw_dir=raw)


# Fixed roster. Add / remove here.
ROSTER: tuple[Filer, ...] = (
    Filer.make("salp",       "0002045724", "Situational Awareness LP"),
    Filer.make("scion",      "0001649339", "Scion Asset Management (Burry)"),
    Filer.make("pabrai",     "0001549575", "Dalal Street LLC (Pabrai)"),
    Filer.make("baupost",    "0001061768", "Baupost Group (Klarman)"),
    Filer.make("pershing",   "0001336528", "Pershing Square (Ackman)"),
    Filer.make("appaloosa",  "0001656456", "Appaloosa LP (Tepper)"),
    Filer.make("thirdpoint", "0001040273", "Third Point (Loeb)"),
    Filer.make("akre",       "0001112520", "Akre Capital (Akre)"),
    Filer.make("harris",     "0000813917", "Harris Associates (Nygren)"),
    Filer.make("oaktree",    "0000949509", "Oaktree Capital (Marks)"),
    Filer.make("berkshire",  "0001067983", "Berkshire Hathaway (Buffett)"),
    Filer.make("duquesne",   "0001536411", "Duquesne FO (Druckenmiller)"),
)


def _build_strategy(filer: Filer, mapping: dict[str, str | None]) -> object:
    pairs = []
    for q in sorted(p for p in filer.raw_dir.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    refs = load_filing_refs(filer.raw_dir)
    cusip_to_ticker = {c: mapping.get(c) for c in panel["issuers"]}
    return follow_the_filer(
        panel,
        filing_refs=refs,
        cusip_to_ticker=cusip_to_ticker,
        manager_cik=filer.cik,
        manager_name=filer.name,
        run_id=f"multi_filer_n:{filer.slug}",
        top_n=25,
    )


def _portfolio_values_for(filer: Filer) -> dict:
    out: dict[date, float] = {}
    for q in sorted(p for p in filer.raw_dir.iterdir() if p.is_dir()):
        meta = parse_primary_doc(q / "primary_doc.xml")
        d = datetime.strptime(meta.period_iso, "%Y-%m-%d").date()
        out[d] = meta.table_value_total
    return {filer.cik: out}


def _resolve_universe() -> dict[str, str | None]:
    all_issuers: dict[str, str] = {}
    for filer in ROSTER:
        if not filer.raw_dir.exists():
            continue
        for q in sorted(p for p in filer.raw_dir.iterdir() if p.is_dir()):
            for h in parse_infotable(q / "infotable.xml"):
                all_issuers[h.cusip] = h.name_of_issuer
    mapping, _ = resolve_tickers(all_issuers, overrides=COMMON_OVERRIDES, sec_tickers_cache=SEC_TICKERS_CACHE)
    # Strip share-class / preferred symbols that Yahoo can't serve.
    return {
        c: t for c, t in mapping.items()
        if t is None or (all(ch.isalnum() for ch in t) and len(t) <= 6)
    }


def main() -> None:
    mapping = _resolve_universe()
    filers = [_build_strategy(f, mapping) for f in ROSTER if f.raw_dir.exists()]
    portfolio_values: dict = {}
    for f in ROSTER:
        if f.raw_dir.exists():
            portfolio_values.update(_portfolio_values_for(f))

    eq = equal_weight(filers)
    vw = value_weight(filers, portfolio_values)
    c2 = consensus(filers, min_overlap=2)
    c3 = consensus(filers, min_overlap=3)

    src = CachingPriceSource(YahooPriceSource(), PRICES_DIR)
    end = date(2026, 4, 26)

    runs: list[tuple[str, object]] = []
    for label, tw in (
        [(f.name, t) for f, t in zip([f for f in ROSTER if f.raw_dir.exists()], filers)]
        + [
            ("Equal-weight (N=12)", eq),
            ("Value-weight (N=12)", vw),
            ("Consensus (>=2 of 12)", c2),
            ("Consensus (>=3 of 12)", c3),
        ]
    ):
        if not tw.snapshots:
            continue
        try:
            res = run_backtest(tw, src, start_cash=1_000_000.0, end_date=end, rebalance_threshold_bps=250.0)
            runs.append((label, res))
        except Exception as e:
            print(f"  SKIP {label}: {type(e).__name__}: {e}")

    # Benchmarks + factor panel.
    all_dates = sorted({d for _, r in runs for d in r.dates})
    spy_bars = src.daily("SPY", all_dates[0], all_dates[-1])
    spy_close = {b.d: b.close for b in spy_bars}
    factors = EtfProxyFactors(src).panel(all_dates[0], all_dates[-1])

    rows: list[dict] = []
    for label, res in runs:
        s = summary(res.dates, res.nav)
        common = [d for d in res.dates if d in spy_close]
        spy_nav = []
        bench = None
        if common:
            base = spy_close[common[0]]
            spy_nav = [res.nav[0] * spy_close[d] / base for d in common]
            bench = benchmark_compare(res.dates, res.nav, common, spy_nav).to_dict()
        fac = factor_decompose(res.dates, res.nav, factors, factors=("mkt_rf", "smb", "hml"))
        rows.append({
            "label": label,
            "summary": s,
            "benchmark": bench,
            "factors": fac,
            "rebalances": len(res.rebalance_dates),
        })

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.with_suffix(".json").write_text(json.dumps(rows, indent=2, default=str))
    md = _format(rows, all_dates[0], all_dates[-1])
    REPORT.write_text(md)
    print(md)


def _format(rows, start, end) -> str:
    lines = [
        f"# Multi-filer backtest comparison (N=12)",
        "",
        f"Window: {start} → {end}",
        "",
        "## Risk and return vs SPY",
        "",
        "| Strategy | Total ret | CAGR | Sharpe | MaxDD | α (annual) | β | InfoRatio |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        s = r["summary"]
        b = r["benchmark"] or {}
        lines.append(
            f"| {r['label']} | {s['total_return']:.1%} | {s['cagr']:.1%} | "
            f"{s['sharpe']:.2f} | {s['max_drawdown']:.1%} | "
            f"{b.get('alpha_annual',0):.1%} | {b.get('beta',0):.2f} | {b.get('info_ratio',0):.2f} |"
        )
    lines += [
        "",
        "## Factor decomposition (ETF-proxy 3-factor)",
        "",
        "Loadings on Mkt-RF (SPY−rf), SMB (IWM−SPY), HML (IWD−IWF). α is",
        "the regression intercept annualized. R² shows how much of the",
        "strategy's variance the factors explain.",
        "",
        "| Strategy | α (annual) | β_mkt | β_smb | β_hml | R² | n |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        f = r["factors"]
        L = f.get("loadings", {})
        lines.append(
            f"| {r['label']} | {f.get('alpha_annual',0):.1%} | "
            f"{L.get('mkt_rf',0):.2f} | {L.get('smb',0):.2f} | {L.get('hml',0):.2f} | "
            f"{f.get('r_squared',0):.2f} | {f.get('n',0)} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- Top-25 positions per filer are kept; smaller positions trimmed for tractability.",
        "- ETF-proxy factors are correlated with but not identical to academic Fama-French. Loadings differ.",
        "- α from SPY-only regression (left table) and 3-factor regression (right table) usually disagree; the 3-factor α is more conservative because SMB / HML absorb size and value tilts that single-factor α attributes to skill.",
        "- Consensus strategies often hold cash heavily because mandate overlap is small; that's a real signal of mandate diversity.",
        "- Yahoo v8 chart data is unofficial; treat differences smaller than ~3% alpha as noise.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
