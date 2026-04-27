"""Backtester tests using the synthetic price source."""
from datetime import date

from wofo.backtest import run_backtest, summary, max_drawdown, sharpe
from wofo.prices import SyntheticPriceSource
from wofo.research.follow_the_filer import TargetWeights, Snapshot


def _two_snapshot_strategy() -> TargetWeights:
    return TargetWeights(
        manager_cik="0000000000",
        manager_name="Test Manager",
        snapshots=[
            Snapshot(
                effective_date=date(2024, 1, 15),
                period_of_report=date(2023, 12, 31),
                weights={"AAA": 0.6, "BBB": 0.4},
                unmapped_value_share=0.0,
                provenance={"test": "snap1"},
            ),
            Snapshot(
                effective_date=date(2024, 7, 15),
                period_of_report=date(2024, 6, 30),
                weights={"AAA": 0.3, "BBB": 0.3, "CCC": 0.4},
                unmapped_value_share=0.0,
                provenance={"test": "snap2"},
            ),
        ],
    )


def test_backtest_runs_and_produces_nav():
    src = SyntheticPriceSource(drift=0.0, vol=0.01)
    res = run_backtest(_two_snapshot_strategy(), src, start_cash=1_000_000.0, end_date=date(2024, 12, 31))
    assert len(res.nav) == len(res.dates) > 100
    # NAV should not be NaN/inf and should be in a reasonable range.
    assert all(v > 0 and v == v for v in res.nav)
    # Two snapshots -> at least two rebalances.
    assert len(res.rebalance_dates) >= 2


def test_backtest_metrics_make_sense():
    src = SyntheticPriceSource(drift=0.0, vol=0.005)
    res = run_backtest(_two_snapshot_strategy(), src, end_date=date(2024, 12, 31))
    s = summary(res.dates, res.nav)
    assert s["n_days"] == len(res.dates)
    # Metrics should be finite numbers.
    assert isinstance(s["sharpe"], float)
    assert 0.0 <= s["max_drawdown"] <= 1.0


def test_unknown_ticker_skipped_not_crashed(monkeypatch):
    src = SyntheticPriceSource()
    # Inject a target with a ticker the synthetic source still happily prices —
    # the synthetic source returns data for any string. To force a NotFound,
    # use a wrapper.
    from wofo.prices import NotFound
    class FlakySource:
        def __init__(self, inner):
            self.inner = inner
        def daily(self, ticker, start, end):
            if ticker == "MISSING":
                raise NotFound(ticker)
            return self.inner.daily(ticker, start, end)

    tw = TargetWeights(
        manager_cik="0", manager_name="t",
        snapshots=[Snapshot(
            effective_date=date(2024, 1, 15),
            period_of_report=date(2023, 12, 31),
            weights={"AAA": 0.5, "MISSING": 0.5},
            unmapped_value_share=0.0,
            provenance={},
        )],
    )
    res = run_backtest(tw, FlakySource(src), end_date=date(2024, 6, 30))
    # The portfolio should still run; cash share should be ~50% because half the target was unbuyable.
    assert max(res.cash_share[10:]) >= 0.4


def test_max_drawdown_known_series():
    nav = [100, 110, 105, 90, 95, 120]
    # peak 110 -> trough 90 -> mdd = (110-90)/110 = 0.1818...
    assert abs(max_drawdown(nav) - (110 - 90) / 110) < 1e-9


def test_sharpe_zero_for_flat_series():
    assert sharpe([100.0] * 200) == 0.0
