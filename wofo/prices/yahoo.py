"""Yahoo Finance v8 chart-API adapter.

Free, no API key. Unofficial — Yahoo can change or rate-limit at any
time, so production deployments should use a paid feed and treat this
as a prototyping / sanity-check source only.

Endpoint:
    https://query1.finance.yahoo.com/v8/finance/chart/{ticker}
        ?interval=1d&period1={start_epoch}&period2={end_epoch}
"""
from __future__ import annotations

import json
import os
import time
from datetime import date, datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .source import NotFound, PriceBar


class YahooPriceSource:
    BASE = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self, *, request_interval_s: float = 0.3, timeout_s: float = 30.0):
        self.request_interval_s = request_interval_s
        self.timeout_s = timeout_s
        self._last_request: float = 0.0

    def _pace(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.request_interval_s:
            time.sleep(self.request_interval_s - elapsed)
        self._last_request = time.monotonic()

    def _fetch(self, url: str) -> dict:
        self._pace()
        ua = os.environ.get("WOFO_HTTP_UA", "Mozilla/5.0 (compatible; wofo-research/0.1)")
        req = Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
        try:
            with urlopen(req, timeout=self.timeout_s) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            if e.code == 404:
                raise NotFound(url) from e
            raise
        except URLError as e:
            raise RuntimeError(f"yahoo fetch failed: {e}") from e

    @staticmethod
    def _epoch(d: date) -> int:
        return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())

    def daily(self, ticker: str, start: date, end: date) -> list[PriceBar]:
        # Yahoo's period2 is exclusive on second resolution; pad by 1 day.
        url = (
            f"{self.BASE}/{ticker}"
            f"?interval=1d&period1={self._epoch(start)}&period2={self._epoch(end) + 86400}"
        )
        payload = self._fetch(url)
        chart = payload.get("chart", {})
        err = chart.get("error")
        if err is not None and err.get("code"):
            if err.get("code") == "Not Found":
                raise NotFound(f"yahoo: ticker not found: {ticker}")
            raise RuntimeError(f"yahoo error: {err}")
        results = chart.get("result") or []
        if not results:
            raise NotFound(f"yahoo: empty result for {ticker}")
        r = results[0]
        ts = r.get("timestamp") or []
        quote = (r.get("indicators", {}).get("quote") or [{}])[0]
        opens = quote.get("open") or []
        highs = quote.get("high") or []
        lows = quote.get("low") or []
        closes = quote.get("close") or []
        vols = quote.get("volume") or []

        bars: list[PriceBar] = []
        for i, t in enumerate(ts):
            o = opens[i] if i < len(opens) else None
            h = highs[i] if i < len(highs) else None
            lo = lows[i] if i < len(lows) else None
            c = closes[i] if i < len(closes) else None
            v = vols[i] if i < len(vols) else None
            if c is None:
                continue  # Yahoo sometimes returns None for non-trading days
            d = datetime.fromtimestamp(t, tz=timezone.utc).date()
            if d < start or d > end:
                continue
            bars.append(
                PriceBar(
                    d=d,
                    open=float(o) if o is not None else float(c),
                    high=float(h) if h is not None else float(c),
                    low=float(lo) if lo is not None else float(c),
                    close=float(c),
                    volume=int(v) if v is not None else 0,
                )
            )
        if not bars:
            raise NotFound(f"yahoo: no bars in window for {ticker}")
        return bars
