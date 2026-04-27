"""Tests for the follow-the-filer strategy + issuer mapping."""
from datetime import date
from pathlib import Path

from wofo.research import follow_the_filer, IssuerOverride
from wofo.research.follow_the_filer import load_filing_refs
from wofo.research.issuer_map import _norm
from wofo.thirteenf import parse_infotable, parse_primary_doc, build_panel


RAW = Path(__file__).resolve().parents[1] / "wofo" / "data" / "13f" / "raw"


def test_norm_strips_corporate_suffixes():
    assert _norm("Constellation Energy Corp") == _norm("Constellation Energy Corporation")
    assert _norm("BLOOM ENERGY CORP") == "bloom energy"
    assert _norm("Lumentum Hldgs Inc") == "lumentum"


def test_follow_the_filer_with_overrides():
    # Manual map covers what we need without hitting the network.
    overrides = IssuerOverride(by_issuer={
        "CONSTELLATION ENERGY CORP": "CEG",
        "MARVELL TECHNOLOGY INC": "MRVL",
        "MODINE MFG CO": "MOD",
        "ANTERIX INC": "ATEX",
        "CIPHER MINING INC": "CIFR",
        "VISTRA CORP": "VST",
    })

    pairs = []
    for q in sorted(p for p in RAW.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    refs = load_filing_refs(RAW)

    # Build cusip -> name from panel issuers, then resolve via overrides only
    # (skip SEC fetch by pre-populating the mapping ourselves).
    cusip_to_ticker: dict[str, str | None] = {}
    for cusip, name in panel["issuers"].items():
        cusip_to_ticker[cusip] = overrides.by_issuer.get(name)

    tw = follow_the_filer(
        panel,
        filing_refs=refs,
        cusip_to_ticker=cusip_to_ticker,
        manager_cik="0002045724",
        manager_name="Situational Awareness LP",
    )
    assert tw.manager_cik == "0002045724"
    assert len(tw.snapshots) == 5
    # First snapshot: most positions will be unmapped because we only added 6 overrides.
    s0 = tw.snapshots[0]
    # Mapped weights + unmapped share == 1.
    assert abs(sum(s0.weights.values()) + s0.unmapped_value_share - 1.0) < 1e-6
    # Effective date should be on or after period-of-report.
    for s in tw.snapshots:
        assert s.effective_date >= s.period_of_report
