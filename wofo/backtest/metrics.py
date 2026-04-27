"""Backtest summary metrics.

No numpy dependency. The math is straightforward and the input series
are short (daily bars over a few years).
"""
from __future__ import annotations

import math
from datetime import date
from typing import Sequence


def _returns(nav: Sequence[float]) -> list[float]:
    rets: list[float] = []
    for i in range(1, len(nav)):
        prev = nav[i - 1]
        rets.append((nav[i] - prev) / prev if prev else 0.0)
    return rets


def cagr(dates: Sequence[date], nav: Sequence[float]) -> float:
    if len(nav) < 2 or nav[0] <= 0:
        return 0.0
    years = max((dates[-1] - dates[0]).days / 365.25, 1e-9)
    return (nav[-1] / nav[0]) ** (1 / years) - 1


def sharpe(nav: Sequence[float], *, rf_annual: float = 0.0, periods_per_year: int = 252) -> float:
    rets = _returns(nav)
    if len(rets) < 2:
        return 0.0
    rf_per = rf_annual / periods_per_year
    excess = [r - rf_per for r in rets]
    mean = sum(excess) / len(excess)
    var = sum((r - mean) ** 2 for r in excess) / (len(excess) - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(periods_per_year)


def max_drawdown(nav: Sequence[float]) -> float:
    """Returns max drawdown as a positive fraction (e.g. 0.25 == 25% peak-to-trough)."""
    peak = -math.inf
    mdd = 0.0
    for v in nav:
        if v > peak:
            peak = v
        if peak > 0:
            dd = (peak - v) / peak
            if dd > mdd:
                mdd = dd
    return mdd


def summary(dates: Sequence[date], nav: Sequence[float]) -> dict:
    return {
        "start_date": dates[0].isoformat() if dates else None,
        "end_date": dates[-1].isoformat() if dates else None,
        "n_days": len(dates),
        "start_nav": nav[0] if nav else 0.0,
        "end_nav": nav[-1] if nav else 0.0,
        "total_return": (nav[-1] / nav[0] - 1) if (nav and nav[0]) else 0.0,
        "cagr": cagr(dates, nav),
        "sharpe": sharpe(nav),
        "max_drawdown": max_drawdown(nav),
    }
