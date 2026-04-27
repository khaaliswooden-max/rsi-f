"""Minimal portfolio backtester.

Takes a `TargetWeights` series and a `PriceSource`, simulates a
periodically rebalanced long-only portfolio, and reports daily NAV +
summary metrics. Intentionally simple — fancier features (transaction
costs beyond a flat bps, slippage models, partial fills) belong in a
dedicated backtest engine; see `docs/repos.md`.
"""
from .portfolio import run_backtest, BacktestResult
from .metrics import summary, sharpe, max_drawdown, cagr

__all__ = ["run_backtest", "BacktestResult", "summary", "sharpe", "max_drawdown", "cagr"]
