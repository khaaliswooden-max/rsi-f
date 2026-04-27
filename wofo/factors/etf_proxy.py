"""ETF-proxy factor model.

Approximates academic factors using free ETF prices:

- Mkt-RF: SPY return - daily T-bill yield (BIL ETF as a rough rf proxy)
- SMB:    IWM (Russell 2000)  return - SPY (S&P 500) return
- HML:    IWD (Russell 1000 Value) - IWF (Russell 1000 Growth)
- RMW:    QUAL (MSCI USA Quality) - SPY  (sign convention: quality -
          market, so it's "robust minus weak" in the regression sense)
- MOM:    MTUM (MSCI USA Momentum) - SPY

Caveats:

1. These are *proxies*, not the academic Fama-French factors. They
   are correlated but not identical and beta loadings will differ.
2. Daily T-bill yield via BIL price is a coarse rf approximation; the
   alpha intercept absorbs the residual mismatch.
3. Coverage starts only as far back as the youngest ETF in the basket.
"""
from __future__ import annotations

from datetime import date

from wofo.prices.source import PriceSource

from .source import FactorPanel, FactorRow


def _series_returns(bars):
    out: dict[date, float] = {}
    prev = None
    for b in bars:
        if prev is not None and prev > 0:
            out[b.d] = (b.close - prev) / prev
        prev = b.close
    return out


class EtfProxyFactors:
    def __init__(self, price_source: PriceSource):
        self.price_source = price_source

    def panel(self, start: date, end: date) -> FactorPanel:
        ps = self.price_source
        spy = _series_returns(ps.daily("SPY", start, end))
        iwm = _series_returns(ps.daily("IWM", start, end))
        iwd = _series_returns(ps.daily("IWD", start, end))
        iwf = _series_returns(ps.daily("IWF", start, end))
        try:
            qual = _series_returns(ps.daily("QUAL", start, end))
        except Exception:
            qual = {}
        try:
            mtum = _series_returns(ps.daily("MTUM", start, end))
        except Exception:
            mtum = {}

        # rf proxy: convert BIL price level into an implied daily yield via
        # short-rate ETF return. BIL holds 1-3mo T-bills; daily price change
        # is dominated by yield accrual minus tiny duration risk. Using the
        # BIL daily return as rf is approximately correct for short windows.
        try:
            bil = _series_returns(ps.daily("BIL", start, end))
        except Exception:
            bil = {}

        common = sorted(set(spy) & set(iwm) & set(iwd) & set(iwf))
        rows: list[FactorRow] = []
        for d in common:
            rf = bil.get(d, 0.0)
            mkt_rf = spy[d] - rf
            smb = iwm[d] - spy[d]
            hml = iwd[d] - iwf[d]
            rmw = (qual.get(d) - spy[d]) if d in qual else None
            mom = (mtum.get(d) - spy[d]) if d in mtum else None
            rows.append(FactorRow(d=d, mkt_rf=mkt_rf, smb=smb, hml=hml, rmw=rmw, mom=mom, rf=rf))
        return FactorPanel(rows=rows, source="etf_proxy", proxy=True)
