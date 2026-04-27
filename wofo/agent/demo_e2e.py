"""End-to-end demo: 13F panel -> follow-the-filer strategy -> synthetic backtest.

Runs entirely offline using `SyntheticPriceSource`, so the resulting
NAV is **not** a real return — it is a sanity check that the plumbing
works. Replace the price source with a real one (Stooq, Polygon, etc.)
to get meaningful numbers.

    python -m wofo.agent.demo_e2e
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from wofo.thirteenf import parse_infotable, parse_primary_doc, build_panel
from wofo.research import IssuerOverride, follow_the_filer
from wofo.research.follow_the_filer import load_filing_refs
from wofo.backtest import run_backtest, summary
from wofo.prices import SyntheticPriceSource


# Hand-curated overrides covering most names that appear in SA LP filings.
# Update as needed; this is a documentation artifact, not a complete map.
DEFAULT_OVERRIDES = IssuerOverride(by_issuer={
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
    "VANECK ETF TRUST": None,    # ETF; mapping is ambiguous without ticker
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
    raw = Path(__file__).resolve().parents[2] / "wofo" / "data" / "13f" / "raw"
    pairs = []
    for q in sorted(p for p in raw.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    refs = load_filing_refs(raw)

    cusip_to_ticker: dict[str, str | None] = {}
    for cusip, name in panel["issuers"].items():
        cusip_to_ticker[cusip] = DEFAULT_OVERRIDES.by_issuer.get(name)

    tw = follow_the_filer(
        panel,
        filing_refs=refs,
        cusip_to_ticker=cusip_to_ticker,
        manager_cik="0002045724",
        manager_name="Situational Awareness LP",
        run_id="demo_e2e",
    )

    print(f"Manager: {tw.manager_name}")
    for s in tw.snapshots:
        mapped_count = len(s.weights)
        print(
            f"  effective {s.effective_date}  report {s.period_of_report}  "
            f"mapped={mapped_count} weight_total={sum(s.weights.values()):.1%} "
            f"unmapped={s.unmapped_value_share:.1%}"
        )

    # Synthetic backtest is a plumbing check, not a real return.
    src = SyntheticPriceSource(drift=0.0004, vol=0.02)
    res = run_backtest(tw, src, start_cash=1_000_000.0, end_date=date(2026, 4, 30))
    s = summary(res.dates, res.nav)
    print()
    print("Synthetic backtest summary (NOT real returns):")
    for k, v in s.items():
        if isinstance(v, float):
            print(f"  {k:<14} {v:>12,.4f}")
        else:
            print(f"  {k:<14} {v}")


if __name__ == "__main__":
    main()
