"""Factor-source protocol shared by all adapters."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class FactorRow:
    d: date
    mkt_rf: float        # market excess return
    smb: float | None    # small minus big
    hml: float | None    # high minus low (value)
    rmw: float | None    # robust minus weak (quality / profitability)
    mom: float | None    # momentum
    rf: float            # risk-free daily rate


@dataclass
class FactorPanel:
    rows: list[FactorRow]
    source: str          # human-readable name of the source
    proxy: bool          # True if factors are ETF-proxy approximations

    def by_date(self) -> dict[date, FactorRow]:
        return {r.d: r for r in self.rows}


@runtime_checkable
class FactorSource(Protocol):
    def panel(self, start: date, end: date) -> FactorPanel: ...
