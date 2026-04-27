"""Price-source protocol shared by all adapters."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable


class NotFound(LookupError):
    """Raised when a ticker is unknown to the source."""


@dataclass(frozen=True)
class PriceBar:
    d: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@runtime_checkable
class PriceSource(Protocol):
    """Daily-bar price source.

    Implementations must be deterministic for a given (ticker, start, end).
    They should raise `NotFound` (not return empty) for unknown tickers so
    callers can distinguish "no data" from "delisted on this date."
    """

    def daily(self, ticker: str, start: date, end: date) -> list[PriceBar]:
        ...
