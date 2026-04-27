# Multi-filer backtest comparison

Window (union of all runs): 2025-02-13 → 2026-04-24

## Strategy comparison

| Strategy | n_days | Total ret | CAGR | Sharpe | MaxDD | α (annual) | β | InfoRatio | UpCap | DnCap | Rebal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SA LP solo | 299 | 94.5% | 75.1% | 1.45 | 35.7% | 42.5% | 1.63 | 1.42 | 2.10 | 1.69 | 31 |
| Scion solo | 299 | -5.2% | -4.4% | -0.04 | 26.3% | -9.3% | 0.54 | -0.64 | 0.85 | 1.01 | 14 |
| Pabrai solo | 300 | 52.0% | 42.1% | 1.10 | 26.2% | 34.9% | 0.52 | 0.72 | 0.78 | 0.41 | 22 |
| Equal-weight 3 | 300 | 51.9% | 42.0% | 1.43 | 21.3% | 25.3% | 0.90 | 1.12 | 1.25 | 1.02 | 24 |
| Value-weight 3 | 300 | 61.4% | 49.5% | 1.31 | 29.2% | 29.1% | 1.17 | 1.12 | 1.63 | 1.38 | 25 |
| Consensus (>=2 managers) | 300 | -2.9% | -2.5% | -0.09 | 10.7% | -3.4% | 0.14 | -0.74 | 0.21 | 0.26 | 11 |

## Notes

- α / β / InfoRatio / UpCap / DnCap are computed against SPY on the trading-day union.
- Rebalances counts both snapshot effective-date forced rebalances and drift-triggered ones (250 bps threshold).
- The three solo books are mandate-orthogonal: SA LP = AI infra / power; Scion = concentrated contrarian; Pabrai = deep-value commodities.
- Consensus (>=2 managers) often returns 0 names because the books have minimal overlap. That is real signal, not a bug — these managers do not agree on much.
- Yahoo v8 chart data is unofficial; treat single-digit alpha differences across strategies as noise.
