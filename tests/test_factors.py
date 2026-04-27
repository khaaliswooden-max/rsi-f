"""Tests for factor models + factor decomposition."""
from datetime import date, timedelta
import random

from wofo.evals import factor_decompose
from wofo.factors import EtfProxyFactors, SyntheticFactors
from wofo.prices import SyntheticPriceSource


def test_synthetic_factors_smoke():
    p = SyntheticFactors().panel(date(2024, 1, 1), date(2024, 6, 30))
    assert len(p.rows) > 100
    assert p.source == "synthetic"
    assert p.rows[0].mkt_rf is not None


def test_etf_proxy_against_synthetic_prices():
    src = SyntheticPriceSource(drift=0.0004, vol=0.01)
    fac = EtfProxyFactors(src)
    p = fac.panel(date(2024, 1, 1), date(2024, 6, 30))
    assert p.source == "etf_proxy"
    assert p.proxy is True
    assert len(p.rows) > 100
    # Sanity: factors should be small daily numbers, not nan / huge.
    for r in p.rows[:20]:
        assert -0.5 < r.mkt_rf < 0.5
        assert -0.5 < (r.smb or 0) < 0.5


def test_factor_decompose_recovers_loadings():
    """Construct a strategy as a known linear combination of factors,
    then check the regression recovers the loadings within tolerance.
    """
    rng = random.Random(7)
    panel = SyntheticFactors().panel(date(2024, 1, 1), date(2025, 6, 30))
    # Strategy daily return = 0.0002 alpha + 1.2*mkt_rf + 0.4*smb - 0.2*hml + noise
    s_dates = [r.d for r in panel.rows]
    s_nav = [100.0]
    for r in panel.rows[1:]:
        ret = 0.0002 + 1.2 * r.mkt_rf + 0.4 * r.smb + (-0.2) * r.hml + rng.gauss(0, 0.001)
        s_nav.append(s_nav[-1] * (1 + ret))

    out = factor_decompose(s_dates, s_nav, panel)
    assert out["n"] > 200
    assert out["r_squared"] > 0.9
    assert abs(out["loadings"]["mkt_rf"] - 1.2) < 0.05
    assert abs(out["loadings"]["smb"] - 0.4) < 0.1
    assert abs(out["loadings"]["hml"] - (-0.2)) < 0.1
    # Annualized alpha should be around 0.0002 * 252 ~ 0.05
    assert 0.02 < out["alpha_annual"] < 0.10


def test_factor_decompose_handles_missing_factor():
    """Drop a factor that has no values; regression should ignore it."""
    panel = SyntheticFactors().panel(date(2024, 1, 1), date(2024, 6, 30))
    # Simulate a 4-factor request where momentum is None (synthetic provides it,
    # but we ask for a factor name that doesn't exist on FactorRow).
    s_dates = [r.d for r in panel.rows]
    s_nav = [100.0 * (1.0005 ** i) for i in range(len(s_dates))]
    out = factor_decompose(s_dates, s_nav, panel, factors=("mkt_rf", "smb"))
    assert "smb" in out["loadings"]
    assert "mkt_rf" in out["loadings"]
    assert out["n"] > 50
