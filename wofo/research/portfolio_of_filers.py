"""Combine multiple filers' books into one strategy.

Three weighting schemes, all of which take in a list of per-manager
`TargetWeights` and emit a single combined `TargetWeights` series:

- `equal_weight`     — each manager gets 1/N of the combined book.
- `value_weight`     — managers weighted by their reported portfolio
                       value at each effective date.
- `consensus`        — only positions held by >= K managers; equal-
                       weight across the survivors.

The combined snapshots' effective dates are the *union* of the
constituent managers' effective dates. On each combined effective date,
we take the most recent snapshot of each manager available on or
before that date.

Caveat: if managers have very different turnover cadences, the
combined series will have many tiny rebalances. The backtester's
drift-threshold mechanism mitigates churn.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from typing import Sequence

from .follow_the_filer import Snapshot, TargetWeights


def _active_at(tw: TargetWeights, d: date) -> Snapshot | None:
    active: Snapshot | None = None
    for s in tw.snapshots:
        if s.effective_date <= d:
            active = s
        else:
            break
    return active


def _union_effective_dates(filers: Sequence[TargetWeights]) -> list[date]:
    dates: set[date] = set()
    for tw in filers:
        for s in tw.snapshots:
            dates.add(s.effective_date)
    return sorted(dates)


def _provenance(filers: Sequence[TargetWeights], scheme: str, params: dict) -> dict:
    return {
        "scheme": scheme,
        "params": params,
        "constituents": [{"cik": tw.manager_cik, "name": tw.manager_name, "n_snapshots": len(tw.snapshots)} for tw in filers],
        "run_ts_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def equal_weight(
    filers: Sequence[TargetWeights],
    *,
    name: str = "equal_weight_portfolio_of_filers",
) -> TargetWeights:
    if not filers:
        raise ValueError("no filers")
    n = len(filers)
    snaps: list[Snapshot] = []
    for d in _union_effective_dates(filers):
        active = [(_active_at(tw, d), tw) for tw in filers]
        active = [(s, tw) for s, tw in active if s is not None]
        if not active:
            continue
        weight_per = 1.0 / n
        combined: dict[str, float] = {}
        unmapped_total = 0.0
        latest_period = max(s.period_of_report for s, _ in active)
        for s, _ in active:
            for t, w in s.weights.items():
                combined[t] = combined.get(t, 0.0) + w * weight_per
            unmapped_total += s.unmapped_value_share * weight_per
        # Managers with no active snapshot yet get cash for their slot.
        cash_for_inactive = (n - len(active)) * weight_per
        unmapped_total += cash_for_inactive
        snaps.append(
            Snapshot(
                effective_date=d,
                period_of_report=latest_period,
                weights=combined,
                unmapped_value_share=unmapped_total,
                provenance=_provenance(filers, "equal_weight", {"n": n}),
            )
        )
    return TargetWeights(manager_cik="POF", manager_name=name, snapshots=snaps)


def value_weight(
    filers: Sequence[TargetWeights],
    portfolio_values: dict[str, dict[date, float]],
    *,
    name: str = "value_weighted_portfolio_of_filers",
) -> TargetWeights:
    """Weight managers by their reported portfolio value at each date.

    `portfolio_values[cik][period_of_report]` -> total reported $ value.
    """
    if not filers:
        raise ValueError("no filers")

    snaps: list[Snapshot] = []
    for d in _union_effective_dates(filers):
        active = [(_active_at(tw, d), tw) for tw in filers]
        active = [(s, tw) for s, tw in active if s is not None]
        if not active:
            continue
        # Total AUM across active managers at this date.
        weights_per: dict[str, float] = {}
        total_aum = 0.0
        for s, tw in active:
            v = (portfolio_values.get(tw.manager_cik, {}) or {}).get(s.period_of_report, 0.0)
            weights_per[tw.manager_cik] = v
            total_aum += v
        if total_aum <= 0:
            # Degenerate; fall back to equal across active.
            for tw in [t for _, t in active]:
                weights_per[tw.manager_cik] = 1.0
            total_aum = float(len(active))

        combined: dict[str, float] = {}
        unmapped_total = 0.0
        latest_period = max(s.period_of_report for s, _ in active)
        for s, tw in active:
            mw = weights_per[tw.manager_cik] / total_aum
            for t, w in s.weights.items():
                combined[t] = combined.get(t, 0.0) + w * mw
            unmapped_total += s.unmapped_value_share * mw
        snaps.append(
            Snapshot(
                effective_date=d,
                period_of_report=latest_period,
                weights=combined,
                unmapped_value_share=unmapped_total,
                provenance=_provenance(filers, "value_weight", {"n": len(filers)}),
            )
        )
    return TargetWeights(manager_cik="POF", manager_name=name, snapshots=snaps)


def consensus(
    filers: Sequence[TargetWeights],
    *,
    min_overlap: int = 2,
    name: str | None = None,
) -> TargetWeights:
    """Equal-weight only tickers held by >= `min_overlap` managers.

    Note: with only 2-3 managers covering disjoint mandates (e.g., AI
    infra vs. distressed coal), consensus may be empty. Document that
    in the report rather than silently returning zero weights.
    """
    if min_overlap < 1:
        raise ValueError("min_overlap must be >= 1")
    if not filers:
        raise ValueError("no filers")
    nm = name or f"consensus_min{min_overlap}_portfolio_of_filers"

    snaps: list[Snapshot] = []
    for d in _union_effective_dates(filers):
        active = [(_active_at(tw, d), tw) for tw in filers]
        active = [(s, tw) for s, tw in active if s is not None]
        if not active:
            continue
        held_by = Counter()
        for s, _ in active:
            for t in s.weights:
                held_by[t] += 1
        survivors = [t for t, c in held_by.items() if c >= min_overlap]
        latest_period = max(s.period_of_report for s, _ in active)
        if not survivors:
            snaps.append(
                Snapshot(
                    effective_date=d,
                    period_of_report=latest_period,
                    weights={},
                    unmapped_value_share=1.0,   # everything in cash
                    provenance=_provenance(filers, "consensus", {"min_overlap": min_overlap, "survivors": 0}),
                )
            )
            continue
        w = 1.0 / len(survivors)
        snaps.append(
            Snapshot(
                effective_date=d,
                period_of_report=latest_period,
                weights={t: w for t in survivors},
                unmapped_value_share=0.0,
                provenance=_provenance(filers, "consensus", {"min_overlap": min_overlap, "survivors": len(survivors)}),
            )
        )
    return TargetWeights(manager_cik="POF", manager_name=nm, snapshots=snaps)
