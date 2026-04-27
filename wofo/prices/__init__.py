"""Pluggable price-data sources.

The agent must work with multiple data vendors over time. Calling code
depends on the `PriceSource` protocol; concrete adapters live alongside.

Built-in adapters:
- `synthetic.SyntheticPriceSource` — deterministic random walk; for tests.
- `stooq.StooqPriceSource` — free daily CSV from stooq.com; for prototyping.

Production deployments should swap in a paid feed (Polygon, Tiingo, etc.)
behind the same protocol.
"""
from .source import PriceSource, PriceBar, NotFound
from .synthetic import SyntheticPriceSource

__all__ = ["PriceSource", "PriceBar", "NotFound", "SyntheticPriceSource"]
