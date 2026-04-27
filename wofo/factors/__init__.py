"""Factor models for performance attribution.

Provides three factor sources behind a common interface:

- `EtfProxyFactors`  — daily factors synthesized from a fixed basket of
  US-equity ETFs. Free, always-on, but a *proxy* for academic
  Fama-French factors (correlated, not identical). This is the
  default.
- `KenFrenchFactors` — adapter for Ken French's published research
  data when reachable. Pulls and caches the daily-factors ZIP from
  Dartmouth.
- `SyntheticFactors`  — deterministic random factors for tests.

All three return `FactorPanel` rows: `(date, mkt_rf, smb, hml, rmw,
mom, rf)`. RMW and MOM are populated only when the source supports
them; the regression in `wofo.evals.signal.factor_decompose` handles
missing factors by ignoring them.
"""
from .source import FactorPanel, FactorRow, FactorSource
from .etf_proxy import EtfProxyFactors
from .synthetic import SyntheticFactors

__all__ = ["FactorPanel", "FactorRow", "FactorSource", "EtfProxyFactors", "SyntheticFactors"]
