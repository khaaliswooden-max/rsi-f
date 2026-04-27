"""Tests for the portfolio-of-filers strategy combinators."""
from datetime import date

from wofo.research import equal_weight, value_weight, consensus
from wofo.research.follow_the_filer import TargetWeights, Snapshot


def _filer(cik: str, name: str, snaps: list[Snapshot]) -> TargetWeights:
    return TargetWeights(manager_cik=cik, manager_name=name, snapshots=snaps)


def _snap(eff: date, period: date, weights: dict, unmapped: float = 0.0) -> Snapshot:
    return Snapshot(
        effective_date=eff, period_of_report=period, weights=weights,
        unmapped_value_share=unmapped, provenance={"t": "test"},
    )


def test_equal_weight_two_filers_same_date():
    a = _filer("A", "A", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"AAA": 1.0})])
    b = _filer("B", "B", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"BBB": 1.0})])
    eq = equal_weight([a, b])
    assert len(eq.snapshots) == 1
    s = eq.snapshots[0]
    assert s.weights == {"AAA": 0.5, "BBB": 0.5}
    assert s.unmapped_value_share == 0.0


def test_equal_weight_inactive_manager_routes_to_cash():
    # A active starting Feb; B not yet (first snapshot in May).
    a = _filer("A", "A", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"AAA": 1.0})])
    b = _filer("B", "B", [_snap(date(2024, 5, 15), date(2024, 3, 31), {"BBB": 1.0})])
    eq = equal_weight([a, b])
    s_feb = eq.snapshots[0]
    # On Feb 14, only A is active; A's slot is 50% in AAA, B's slot is cash.
    assert s_feb.weights == {"AAA": 0.5}
    assert abs(s_feb.unmapped_value_share - 0.5) < 1e-9
    s_may = eq.snapshots[1]
    assert set(s_may.weights) == {"AAA", "BBB"}
    assert abs(sum(s_may.weights.values()) - 1.0) < 1e-9


def test_value_weight_proportional_to_aum():
    a = _filer("A", "A", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"AAA": 1.0})])
    b = _filer("B", "B", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"BBB": 1.0})])
    pv = {
        "A": {date(2023, 12, 31): 100_000_000},
        "B": {date(2023, 12, 31): 900_000_000},
    }
    vw = value_weight([a, b], pv)
    s = vw.snapshots[0]
    assert abs(s.weights["AAA"] - 0.10) < 1e-9
    assert abs(s.weights["BBB"] - 0.90) < 1e-9


def test_consensus_keeps_only_overlap():
    a = _filer("A", "A", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"AAA": 0.5, "XYZ": 0.5})])
    b = _filer("B", "B", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"BBB": 0.5, "XYZ": 0.5})])
    cs = consensus([a, b], min_overlap=2)
    s = cs.snapshots[0]
    assert s.weights == {"XYZ": 1.0}
    assert s.unmapped_value_share == 0.0


def test_consensus_no_overlap_full_cash():
    a = _filer("A", "A", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"AAA": 1.0})])
    b = _filer("B", "B", [_snap(date(2024, 2, 14), date(2023, 12, 31), {"BBB": 1.0})])
    cs = consensus([a, b], min_overlap=2)
    s = cs.snapshots[0]
    assert s.weights == {}
    assert s.unmapped_value_share == 1.0


def test_combined_effective_dates_are_union():
    a = _filer("A", "A", [
        _snap(date(2024, 2, 14), date(2023, 12, 31), {"AAA": 1.0}),
        _snap(date(2024, 5, 15), date(2024, 3, 31), {"AAA": 1.0}),
    ])
    b = _filer("B", "B", [_snap(date(2024, 8, 14), date(2024, 6, 30), {"BBB": 1.0})])
    eq = equal_weight([a, b])
    assert [s.effective_date for s in eq.snapshots] == [
        date(2024, 2, 14), date(2024, 5, 15), date(2024, 8, 14),
    ]
