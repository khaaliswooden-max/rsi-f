"""Research strategy modules.

Strategies turn parsed filing/data panels into dated, provenance-stamped
target-weight series that backtest and paper-trade modules consume.
"""
from .follow_the_filer import follow_the_filer, TargetWeights, Snapshot
from .issuer_map import resolve_tickers, IssuerOverride

__all__ = [
    "follow_the_filer",
    "TargetWeights",
    "Snapshot",
    "resolve_tickers",
    "IssuerOverride",
]
