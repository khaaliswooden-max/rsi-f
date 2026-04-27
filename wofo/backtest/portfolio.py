"""Portfolio backtester: target weights + price source -> daily NAV."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Sequence

from wofo.prices import PriceSource, NotFound
from wofo.research import TargetWeights, Snapshot


@dataclass
class BacktestResult:
    dates: list[date]
    nav: list[float]                  # portfolio value indexed to start_cash
    weights_history: list[dict[str, float]]  # per-day actual weights
    rebalance_dates: list[date]
    skipped_tickers: dict[date, list[str]] = field(default_factory=dict)
    cash_share: list[float] = field(default_factory=list)


def _build_price_panel(
    tickers: set[str],
    start: date,
    end: date,
    source: PriceSource,
) -> tuple[dict[date, dict[str, float]], dict[str, list]]:
    """Pull daily closes for each ticker; return {date: {ticker: close}} aligned."""
    raw: dict[str, dict[date, float]] = {}
    missing: list[str] = []
    for t in sorted(tickers):
        try:
            bars = source.daily(t, start, end)
        except NotFound:
            missing.append(t)
            continue
        raw[t] = {b.d: b.close for b in bars}
    # Trading-day axis = union of dates seen in any series.
    all_dates = sorted({d for series in raw.values() for d in series})
    panel: dict[date, dict[str, float]] = {}
    for d in all_dates:
        panel[d] = {}
        for t, series in raw.items():
            if d in series:
                panel[d][t] = series[d]
    return panel, {"missing_tickers": missing}


def _active_snapshot(snapshots: Sequence[Snapshot], d: date) -> Snapshot | None:
    """Most recent snapshot whose effective_date <= d."""
    active: Snapshot | None = None
    for s in snapshots:
        if s.effective_date <= d:
            active = s
        else:
            break
    return active


def run_backtest(
    target_weights: TargetWeights,
    price_source: PriceSource,
    *,
    start_cash: float = 1_000_000.0,
    rebalance_threshold_bps: float = 50.0,  # rebalance if any weight drifts > this many bps from target
    cost_bps: float = 5.0,                  # round-trip-ish slippage+commission per side
    end_date: date | None = None,
) -> BacktestResult:
    """Run the backtest.

    Behavior:
    - Start with `start_cash` in cash on the first effective_date.
    - On each new snapshot's effective_date, mark the new target.
    - Between snapshots, rebalance only if any target ticker drifts beyond
      the threshold from its target.
    - Tickers in the target that the price source doesn't know are
      *skipped*; their target weight is reallocated to cash for that
      snapshot.
    """
    if not target_weights.snapshots:
        raise ValueError("no snapshots")

    snapshots = sorted(target_weights.snapshots, key=lambda s: s.effective_date)
    start = snapshots[0].effective_date
    end = end_date or (snapshots[-1].effective_date + timedelta(days=365))
    all_tickers = {t for s in snapshots for t in s.weights}

    panel, meta = _build_price_panel(all_tickers, start, end, price_source)
    missing = set(meta["missing_tickers"])

    if not panel:
        raise RuntimeError("price source returned no data for any ticker")

    cash = start_cash
    holdings: dict[str, float] = {}  # ticker -> shares
    out = BacktestResult(dates=[], nav=[], weights_history=[], rebalance_dates=[])

    last_target_id: int | None = None
    for d in sorted(panel):
        prices = panel[d]
        # Mark to market
        nav_val = cash + sum(sh * prices.get(t, _last_close(panel, t, d)) for t, sh in holdings.items())

        snap = _active_snapshot(snapshots, d)
        if snap is None:
            out.dates.append(d); out.nav.append(nav_val); out.weights_history.append({}); out.cash_share.append(1.0)
            continue

        # Filter snapshot to tickers we have *some* prices for and a price today.
        tradable_targets = {t: w for t, w in snap.weights.items() if t in panel.get(d, {}) and t not in missing}
        skipped_today = sorted(set(snap.weights) - set(tradable_targets))
        if skipped_today:
            out.skipped_tickers[d] = skipped_today

        # Renormalize after dropping unknown / no-price-today tickers; balance to cash.
        target_norm_total = sum(tradable_targets.values()) or 0
        # Note: we do NOT renormalize to 1; missing weight stays in cash.

        snap_id = id(snap)
        is_new_snapshot = snap_id != last_target_id
        last_target_id = snap_id

        # Compute current weights (excluding cash).
        current_w = {t: (sh * prices.get(t, _last_close(panel, t, d))) / nav_val for t, sh in holdings.items()}
        max_drift_bps = max(
            (abs(current_w.get(t, 0.0) - tradable_targets.get(t, 0.0)) for t in set(current_w) | set(tradable_targets)),
            default=0.0,
        ) * 10_000

        should_rebalance = is_new_snapshot or max_drift_bps > rebalance_threshold_bps
        if should_rebalance:
            # Liquidate everything to cash, then buy targets.
            for t, sh in holdings.items():
                px = prices.get(t, _last_close(panel, t, d))
                cash += sh * px
                cash -= abs(sh * px) * (cost_bps / 10_000)
            holdings = {}
            for t, w in tradable_targets.items():
                px = prices[t]
                target_dollars = nav_val * w
                shares = target_dollars / px
                cost = abs(target_dollars) * (cost_bps / 10_000)
                holdings[t] = shares
                cash -= target_dollars + cost
            out.rebalance_dates.append(d)
            # Recompute NAV after costs.
            nav_val = cash + sum(sh * prices.get(t, _last_close(panel, t, d)) for t, sh in holdings.items())

        actual_w = {t: (sh * prices.get(t, _last_close(panel, t, d))) / nav_val for t, sh in holdings.items()}
        cash_w = cash / nav_val if nav_val else 1.0
        out.dates.append(d)
        out.nav.append(nav_val)
        out.weights_history.append(actual_w)
        out.cash_share.append(cash_w)

    return out


def _last_close(panel: dict[date, dict[str, float]], ticker: str, d: date) -> float:
    """Most-recent close on or before `d`. 0 if never seen (fully out)."""
    cur = d
    for _ in range(10):  # short walk-back; enough for weekends/holidays
        cur -= timedelta(days=1)
        if cur in panel and ticker in panel[cur]:
            return panel[cur][ticker]
    return 0.0
