"""Deterministic synthetic factors for tests."""
from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta

from .source import FactorPanel, FactorRow


class SyntheticFactors:
    def __init__(self, seed: str = "wofo-test"):
        self.seed = int(hashlib.sha256(seed.encode()).hexdigest()[:12], 16)

    def panel(self, start: date, end: date) -> FactorPanel:
        rng = random.Random(self.seed)
        rows: list[FactorRow] = []
        d = start
        while d <= end:
            if d.weekday() < 5:
                rows.append(
                    FactorRow(
                        d=d,
                        mkt_rf=rng.gauss(0.0004, 0.012),
                        smb=rng.gauss(0.0, 0.005),
                        hml=rng.gauss(0.0, 0.005),
                        rmw=rng.gauss(0.0, 0.004),
                        mom=rng.gauss(0.0, 0.006),
                        rf=0.0001,
                    )
                )
            d += timedelta(days=1)
        return FactorPanel(rows=rows, source="synthetic", proxy=False)
