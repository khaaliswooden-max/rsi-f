"""Deterministic synthetic price source for tests / offline development.

The price path is a seeded random walk. Same (ticker, start, end) always
returns the same series, which lets backtests be reproducible without
network access.
"""
from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta

from .source import PriceBar, PriceSource


class SyntheticPriceSource:
    """Random-walk prices with per-ticker seeded reproducibility."""

    def __init__(self, *, drift: float = 0.0003, vol: float = 0.02, start_price: float = 100.0):
        self.drift = drift
        self.vol = vol
        self.start_price = start_price

    def _seed(self, ticker: str) -> int:
        return int(hashlib.sha256(ticker.encode()).hexdigest()[:12], 16)

    def daily(self, ticker: str, start: date, end: date) -> list[PriceBar]:
        if end < start:
            raise ValueError("end < start")
        rng = random.Random(self._seed(ticker))
        bars: list[PriceBar] = []
        price = self.start_price
        d = start
        while d <= end:
            # Skip weekends to mimic NYSE calendar (rough — does not skip holidays).
            if d.weekday() < 5:
                shock = rng.gauss(self.drift, self.vol)
                price = max(0.01, price * (1 + shock))
                hi = price * (1 + abs(rng.gauss(0, self.vol / 4)))
                lo = price * (1 - abs(rng.gauss(0, self.vol / 4)))
                op = lo + (hi - lo) * rng.random()
                bars.append(
                    PriceBar(
                        d=d,
                        open=round(op, 4),
                        high=round(hi, 4),
                        low=round(lo, 4),
                        close=round(price, 4),
                        volume=rng.randint(100_000, 10_000_000),
                    )
                )
            d += timedelta(days=1)
        return bars


# Self-check that this satisfies the protocol.
_: PriceSource = SyntheticPriceSource()
