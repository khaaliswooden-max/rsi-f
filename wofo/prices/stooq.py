"""Stooq.com daily-CSV adapter.

Free, no API key. Reasonable for prototyping; not appropriate for
production trading. Stooq's coverage and corporate-action handling are
not as clean as paid feeds.

URL pattern:
    https://stooq.com/q/d/l/?s={symbol}&i=d&d1=YYYYMMDD&d2=YYYYMMDD

US tickers need a `.us` suffix on stooq.
"""
from __future__ import annotations

import csv
import io
import os
import time
from datetime import date, datetime
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .source import NotFound, PriceBar


class StooqPriceSource:
    BASE = "https://stooq.com/q/d/l/"

    def __init__(self, *, suffix: str = ".us", request_interval_s: float = 0.25, timeout_s: float = 30.0):
        self.suffix = suffix
        self.request_interval_s = request_interval_s
        self.timeout_s = timeout_s
        self._last_request: float = 0.0

    def _pace(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.request_interval_s:
            time.sleep(self.request_interval_s - elapsed)
        self._last_request = time.monotonic()

    def _fetch(self, url: str) -> str:
        self._pace()
        ua = os.environ.get("WOFO_HTTP_UA", "wofo-research/0.1")
        req = Request(url, headers={"User-Agent": ua})
        try:
            with urlopen(req, timeout=self.timeout_s) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except HTTPError as e:
            if e.code == 404:
                raise NotFound(url) from e
            raise
        except URLError as e:
            raise RuntimeError(f"stooq fetch failed: {e}") from e

    def daily(self, ticker: str, start: date, end: date) -> list[PriceBar]:
        symbol = ticker.lower()
        if "." not in symbol:
            symbol += self.suffix
        url = (
            f"{self.BASE}?s={symbol}&i=d"
            f"&d1={start.strftime('%Y%m%d')}&d2={end.strftime('%Y%m%d')}"
        )
        body = self._fetch(url)
        # Stooq returns "No data" or empty for unknown / out-of-range queries.
        if not body or body.startswith("No data") or "Date,Open" not in body:
            raise NotFound(f"stooq: no data for {ticker} {start}..{end}")
        bars: list[PriceBar] = []
        reader = csv.DictReader(io.StringIO(body))
        for row in reader:
            try:
                bars.append(
                    PriceBar(
                        d=datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=float(row["Close"]),
                        volume=int(float(row.get("Volume") or 0)),
                    )
                )
            except (ValueError, KeyError):
                continue
        return bars
