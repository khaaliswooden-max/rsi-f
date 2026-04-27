"""Filesystem-cached price source wrapper.

Wraps any `PriceSource` with a CSV cache so re-runs do not re-fetch.
Cache key is `(ticker, start, end)` — note that this is conservative
on purpose: a request for 2020-2024 and a separate request for
2020-2025 produce two cache entries. Use one consistent window per
analysis to maximize hits.

Cache layout:
    cache_dir/
      {ticker}_{start}_{end}.csv      Date,Open,High,Low,Close,Volume
"""
from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from .source import NotFound, PriceBar, PriceSource


class CachingPriceSource:
    def __init__(self, inner: PriceSource, cache_dir: str | Path):
        self.inner = inner
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, ticker: str, start: date, end: date) -> Path:
        safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in ticker.upper())
        return self.cache_dir / f"{safe}_{start.isoformat()}_{end.isoformat()}.csv"

    def _read(self, p: Path) -> list[PriceBar]:
        bars: list[PriceBar] = []
        with p.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                bars.append(
                    PriceBar(
                        d=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=int(row["Volume"]),
                    )
                )
        return bars

    def _write(self, p: Path, bars: list[PriceBar]) -> None:
        with p.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
            for b in bars:
                w.writerow([b.d.isoformat(), b.open, b.high, b.low, b.close, b.volume])

    def daily(self, ticker: str, start: date, end: date) -> list[PriceBar]:
        p = self._path(ticker, start, end)
        miss_marker = p.with_suffix(".notfound")
        if p.exists():
            return self._read(p)
        if miss_marker.exists():
            raise NotFound(f"{ticker} (cached miss)")
        try:
            bars = self.inner.daily(ticker, start, end)
        except NotFound:
            miss_marker.touch()
            raise
        self._write(p, bars)
        return bars
