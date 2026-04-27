"""Tests for the 13F pipeline using committed sample data."""
from pathlib import Path

from wofo.thirteenf import parse_infotable, parse_primary_doc, build_panel, qoq_changes, concentration

RAW = Path(__file__).resolve().parents[1] / "wofo" / "data" / "13f" / "raw"


def test_parse_2024q4_meta():
    m = parse_primary_doc(RAW / "2024Q4" / "primary_doc.xml")
    assert m.cik == "0002045724"
    assert m.manager_name == "Situational Awareness LP"
    assert m.period_iso == "2024-12-31"
    assert m.crd_number == "000333011"
    assert m.sec_file_number == "801-132039"
    assert m.is_amendment is False


def test_parse_2024q4_holdings_match_summary():
    m = parse_primary_doc(RAW / "2024Q4" / "primary_doc.xml")
    h = parse_infotable(RAW / "2024Q4" / "infotable.xml")
    assert len(h) == m.table_entry_total
    assert sum(x.value_usd for x in h) == m.table_value_total


def test_panel_periods_sorted_and_unique():
    pairs = []
    for q in sorted(p for p in RAW.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    assert panel["periods"] == sorted(set(panel["periods"]))
    assert len(panel["periods"]) == 5


def test_qoq_initial_period():
    pairs = []
    for q in sorted(p for p in RAW.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    deltas = qoq_changes(panel)
    initials = [d for d in deltas if d["period"] == panel["periods"][0]]
    assert all(d["action"] == "INITIAL" for d in initials)
    # Every position in the first quarter should be classified.
    assert {d["cusip"] for d in initials} == {c for (p, c) in panel["rows"] if p == panel["periods"][0]}


def test_concentration_monotonic_aum():
    pairs = []
    for q in sorted(p for p in RAW.iterdir() if p.is_dir()):
        pairs.append((parse_primary_doc(q / "primary_doc.xml"), parse_infotable(q / "infotable.xml")))
    panel = build_panel(pairs)
    conc = concentration(panel)
    aums = [conc[p]["total_value_usd"] for p in panel["periods"]]
    # SA LP grew every quarter in the sample window; if this changes when re-pulled,
    # this test should be updated, not silenced.
    assert all(b > a for a, b in zip(aums, aums[1:])), aums
