"""Quantitative signal evals.

Inputs are aligned (date, NAV) series — the strategy and the benchmark
on the same trading-day axis. All math is plain Python; no numpy.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import date
from typing import Sequence


def _returns(nav: Sequence[float]) -> list[float]:
    return [(nav[i] - nav[i - 1]) / nav[i - 1] if nav[i - 1] else 0.0 for i in range(1, len(nav))]


def _align(
    s_dates: Sequence[date], s_nav: Sequence[float],
    b_dates: Sequence[date], b_nav: Sequence[float],
) -> tuple[list[date], list[float], list[float]]:
    s = dict(zip(s_dates, s_nav))
    b = dict(zip(b_dates, b_nav))
    common = sorted(set(s) & set(b))
    return common, [s[d] for d in common], [b[d] for d in common]


def info_ratio(
    s_dates: Sequence[date], s_nav: Sequence[float],
    b_dates: Sequence[date], b_nav: Sequence[float],
    *, periods_per_year: int = 252,
) -> float:
    """Annualized active-return mean / active-return stdev."""
    _, s, b = _align(s_dates, s_nav, b_dates, b_nav)
    sr, br = _returns(s), _returns(b)
    if len(sr) < 2:
        return 0.0
    active = [a - c for a, c in zip(sr, br)]
    mean = sum(active) / len(active)
    var = sum((x - mean) ** 2 for x in active) / (len(active) - 1)
    sd = math.sqrt(var)
    return (mean / sd) * math.sqrt(periods_per_year) if sd else 0.0


def jensens_alpha(
    s_dates: Sequence[date], s_nav: Sequence[float],
    b_dates: Sequence[date], b_nav: Sequence[float],
    *, rf_annual: float = 0.0, periods_per_year: int = 252,
) -> dict:
    """OLS regression of strategy excess returns on benchmark excess returns.

    Returns alpha (annualized), beta, and R-squared. No statsmodels — this
    is a textbook two-variable regression.
    """
    _, s, b = _align(s_dates, s_nav, b_dates, b_nav)
    sr, br = _returns(s), _returns(b)
    if len(sr) < 2:
        return {"alpha_annual": 0.0, "beta": 0.0, "r_squared": 0.0, "n": 0}
    rf = rf_annual / periods_per_year
    x = [r - rf for r in br]   # benchmark excess
    y = [r - rf for r in sr]   # strategy excess
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (n - 1)
    var_x = sum((xi - mx) ** 2 for xi in x) / (n - 1)
    var_y = sum((yi - my) ** 2 for yi in y) / (n - 1)
    beta = cov / var_x if var_x else 0.0
    alpha_per = my - beta * mx
    alpha_annual = alpha_per * periods_per_year
    r2 = (cov * cov) / (var_x * var_y) if var_x and var_y else 0.0
    return {"alpha_annual": alpha_annual, "beta": beta, "r_squared": r2, "n": n}


def capture_ratios(
    s_dates: Sequence[date], s_nav: Sequence[float],
    b_dates: Sequence[date], b_nav: Sequence[float],
) -> dict:
    """Up- and down-market capture vs the benchmark."""
    _, s, b = _align(s_dates, s_nav, b_dates, b_nav)
    sr, br = _returns(s), _returns(b)
    up_s, up_b, dn_s, dn_b = 0.0, 0.0, 0.0, 0.0
    for a, c in zip(sr, br):
        if c > 0:
            up_s += a
            up_b += c
        elif c < 0:
            dn_s += a
            dn_b += c
    return {
        "up_capture": (up_s / up_b) if up_b else 0.0,
        "down_capture": (dn_s / dn_b) if dn_b else 0.0,
    }


@dataclass
class SignalEvalResult:
    n_days: int
    total_return_strategy: float
    total_return_benchmark: float
    cagr_strategy: float
    cagr_benchmark: float
    info_ratio: float
    alpha_annual: float
    beta: float
    r_squared: float
    up_capture: float
    down_capture: float
    max_drawdown_strategy: float
    max_drawdown_benchmark: float

    def to_dict(self) -> dict:
        return asdict(self)


def benchmark_compare(
    s_dates: Sequence[date], s_nav: Sequence[float],
    b_dates: Sequence[date], b_nav: Sequence[float],
    *, periods_per_year: int = 252,
) -> SignalEvalResult:
    common, s, b = _align(s_dates, s_nav, b_dates, b_nav)
    if len(common) < 2:
        return SignalEvalResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    s_ret = s[-1] / s[0] - 1
    b_ret = b[-1] / b[0] - 1
    years = max((common[-1] - common[0]).days / 365.25, 1e-9)
    s_cagr = (s[-1] / s[0]) ** (1 / years) - 1 if s[0] else 0.0
    b_cagr = (b[-1] / b[0]) ** (1 / years) - 1 if b[0] else 0.0
    ja = jensens_alpha(s_dates, s_nav, b_dates, b_nav, periods_per_year=periods_per_year)
    cap = capture_ratios(s_dates, s_nav, b_dates, b_nav)
    return SignalEvalResult(
        n_days=len(common),
        total_return_strategy=s_ret,
        total_return_benchmark=b_ret,
        cagr_strategy=s_cagr,
        cagr_benchmark=b_cagr,
        info_ratio=info_ratio(s_dates, s_nav, b_dates, b_nav, periods_per_year=periods_per_year),
        alpha_annual=ja["alpha_annual"],
        beta=ja["beta"],
        r_squared=ja["r_squared"],
        up_capture=cap["up_capture"],
        down_capture=cap["down_capture"],
        max_drawdown_strategy=_mdd(s),
        max_drawdown_benchmark=_mdd(b),
    )


def _mdd(nav: Sequence[float]) -> float:
    peak = -math.inf
    mdd = 0.0
    for v in nav:
        if v > peak:
            peak = v
        if peak > 0:
            mdd = max(mdd, (peak - v) / peak)
    return mdd


def factor_decompose(
    s_dates: Sequence[date],
    s_nav: Sequence[float],
    factor_panel,
    *,
    factors: Sequence[str] = ("mkt_rf", "smb", "hml"),
    periods_per_year: int = 252,
) -> dict:
    """Multivariate OLS regression of strategy excess returns on factor returns.

    Returns dict with `alpha_annual`, `loadings` (dict of factor name ->
    beta), `r_squared`, `n`, `t_stats` (Newey-West-style is overkill for
    a few hundred bars; we report classical t-stats).

    Pure Python; no numpy. Solves the normal equations via Gauss-Jordan.
    """
    by_date = factor_panel.by_date()
    # Strategy daily returns aligned with available factor rows.
    rets: list[float] = []
    Xrows: list[list[float]] = []
    rfs: list[float] = []
    for i in range(1, len(s_dates)):
        d = s_dates[i]
        if d not in by_date or s_nav[i - 1] <= 0:
            continue
        fr = by_date[d]
        x = []
        skip = False
        for f in factors:
            v = getattr(fr, f, None)
            if v is None:
                skip = True
                break
            x.append(v)
        if skip:
            continue
        rets.append((s_nav[i] - s_nav[i - 1]) / s_nav[i - 1])
        Xrows.append([1.0] + x)   # intercept term
        rfs.append(fr.rf)

    n = len(rets)
    k = len(factors) + 1
    if n < k + 5:
        return {"alpha_annual": 0.0, "loadings": {}, "r_squared": 0.0, "n": n, "t_stats": {}}

    y = [r - rf for r, rf in zip(rets, rfs)]   # strategy excess returns
    coefs = _ols(Xrows, y)

    # R^2 and t-stats
    yhat = [sum(c * x for c, x in zip(coefs, row)) for row in Xrows]
    resid = [yi - yh for yi, yh in zip(y, yhat)]
    mean_y = sum(y) / n
    ss_tot = sum((yi - mean_y) ** 2 for yi in y) or 1e-12
    ss_res = sum(r * r for r in resid) or 0.0
    r2 = 1 - ss_res / ss_tot
    sigma2 = ss_res / (n - k) if n > k else 0.0
    XtX_inv = _matrix_inverse(_matmul(_transpose(Xrows), Xrows))
    se = [math.sqrt(sigma2 * XtX_inv[i][i]) if XtX_inv[i][i] > 0 else 0.0 for i in range(k)]
    t_stats = {f: (coefs[i + 1] / se[i + 1] if se[i + 1] else 0.0) for i, f in enumerate(factors)}
    t_stats["alpha"] = coefs[0] / se[0] if se[0] else 0.0

    return {
        "alpha_daily": coefs[0],
        "alpha_annual": coefs[0] * periods_per_year,
        "loadings": {f: coefs[i + 1] for i, f in enumerate(factors)},
        "r_squared": r2,
        "n": n,
        "t_stats": t_stats,
        "factor_source": factor_panel.source,
        "factor_proxy": factor_panel.proxy,
    }


# --- Tiny linear algebra (avoids the numpy dependency) ---------------------


def _transpose(M):
    return [list(row) for row in zip(*M)]


def _matmul(A, B):
    Bt = _transpose(B)
    return [[sum(a * b for a, b in zip(rowA, colB)) for colB in Bt] for rowA in A]


def _matrix_inverse(M):
    n = len(M)
    A = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(M)]
    for i in range(n):
        # Pivot
        pivot = max(range(i, n), key=lambda r: abs(A[r][i]))
        A[i], A[pivot] = A[pivot], A[i]
        if abs(A[i][i]) < 1e-12:
            # Singular — return zeros to signal degenerate fit.
            return [[0.0] * n for _ in range(n)]
        f = A[i][i]
        A[i] = [v / f for v in A[i]]
        for r in range(n):
            if r == i:
                continue
            f = A[r][i]
            A[r] = [a - f * b for a, b in zip(A[r], A[i])]
    return [row[n:] for row in A]


def _ols(X, y):
    Xt = _transpose(X)
    XtX = _matmul(Xt, X)
    XtX_inv = _matrix_inverse(XtX)
    Xty = [sum(Xt[i][j] * y[j] for j in range(len(y))) for i in range(len(Xt))]
    return [sum(XtX_inv[i][j] * Xty[j] for j in range(len(Xty))) for i in range(len(XtX_inv))]
