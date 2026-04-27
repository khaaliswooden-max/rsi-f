# Real-price backtest — follow Situational Awareness LP

Manager CIK: `0002045724`
Snapshots: 5
Start cash: $1,000,000
Window: 2025-02-14 → 2026-04-24 (299 trading days)

## Strategy vs SPY

| Metric | Strategy | SPY (buy & hold) |
|---|---:|---:|
| End NAV | $1,944,784 | $1,170,585 |
| Total return | 94.5% | 17.1% |
| CAGR | 75.1% | 14.2% |
| Sharpe | 1.45 | 0.80 |
| Max drawdown | 35.7% | 19.0% |

## Rebalances (31 total)

Snapshot effective dates (these are forced rebalances on each new filing):

- 2025-02-14 (snapshot)
- 2025-05-15 (snapshot)
- 2025-08-13 (snapshot)
- 2025-08-14 (snapshot)
- 2025-11-14 (snapshot)
- 2026-02-17 (snapshot)

Plus 25 drift-triggered rebalances (threshold 250 bps).

## Caveats

- 13F is long-only and stale by ~45 days (we use file_date as effective).
- Yahoo v8 chart data is unofficial; corporate-action handling is not institutional-grade.
- Some SA LP names (CRWV, SNDK, GLXY, WYFI) listed mid-window; the backtester held cash for those weights until they were tradable.
- Sharpe assumes 0 risk-free rate; flip the rf_annual arg for a different baseline.
