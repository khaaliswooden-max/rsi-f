# Multi-filer backtest comparison (N=12)

Window: 2025-02-10 → 2026-04-24

## Risk and return vs SPY

| Strategy | Total ret | CAGR | Sharpe | MaxDD | α (annual) | β | InfoRatio |
|---|---:|---:|---:|---:|---:|---:|---:|
| Situational Awareness LP | 113.1% | 89.1% | 1.43 | 46.0% | 47.0% | 2.15 | 1.47 |
| Scion Asset Management (Burry) | -4.3% | -3.7% | 0.05 | 31.2% | -14.3% | 1.05 | -0.52 |
| Dalal Street LLC (Pabrai) | 51.6% | 41.8% | 1.10 | 26.2% | 34.7% | 0.52 | 0.71 |
| Baupost Group (Klarman) | 30.6% | 25.1% | 1.34 | 14.2% | 12.6% | 0.76 | 0.78 |
| Pershing Square (Ackman) | 13.6% | 13.3% | 0.84 | 15.7% | -14.5% | 0.92 | -1.51 |
| Appaloosa LP (Tepper) | 20.9% | 17.1% | 0.76 | 23.3% | 1.6% | 1.11 | 0.24 |
| Third Point (Loeb) | 3.3% | 2.7% | 0.24 | 19.7% | -10.2% | 0.98 | -1.63 |
| Akre Capital (Akre) | -15.2% | -12.9% | -0.54 | 25.1% | -25.1% | 0.90 | -1.99 |
| Harris Associates (Nygren) | 0.5% | 0.4% | 0.12 | 21.3% | -11.1% | 0.89 | -1.23 |
| Oaktree Capital (Marks) | 45.8% | 37.1% | 1.75 | 17.0% | 21.6% | 0.75 | 1.28 |
| Berkshire Hathaway (Buffett) | 7.5% | 6.3% | 0.41 | 20.5% | -5.0% | 0.86 | -0.67 |
| Duquesne FO (Druckenmiller) | 28.6% | 23.6% | 1.03 | 23.2% | 7.8% | 1.08 | 0.76 |
| Equal-weight (N=12) | 24.7% | 20.2% | 1.07 | 19.4% | 5.8% | 0.92 | 0.62 |
| Value-weight (N=12) | 7.2% | 6.0% | 0.41 | 20.3% | -6.1% | 0.87 | -0.93 |
| Consensus (>=2 of 12) | 15.1% | 12.5% | 0.68 | 19.6% | -1.9% | 1.01 | -0.24 |
| Consensus (>=3 of 12) | 19.2% | 15.8% | 0.68 | 26.2% | -1.8% | 1.28 | 0.21 |

## Factor decomposition (ETF-proxy 3-factor)

Loadings on Mkt-RF (SPY−rf), SMB (IWM−SPY), HML (IWD−IWF). α is
the regression intercept annualized. R² shows how much of the
strategy's variance the factors explain.

| Strategy | α (annual) | β_mkt | β_smb | β_hml | R² | n |
|---|---:|---:|---:|---:|---:|---:|
| Situational Awareness LP | 51.0% | 1.42 | 1.54 | -1.54 | 0.65 | 298 |
| Scion Asset Management (Burry) | -12.5% | 0.77 | 0.56 | -0.62 | 0.42 | 298 |
| Dalal Street LLC (Pabrai) | 29.9% | 0.56 | 0.92 | 0.23 | 0.15 | 299 |
| Baupost Group (Klarman) | 9.1% | 0.94 | 0.21 | 0.44 | 0.77 | 299 |
| Pershing Square (Ackman) | -15.3% | 0.84 | 0.28 | -0.02 | 0.57 | 256 |
| Appaloosa LP (Tepper) | 3.1% | 0.94 | 0.28 | -0.37 | 0.73 | 302 |
| Third Point (Loeb) | -10.4% | 0.92 | 0.23 | -0.11 | 0.91 | 298 |
| Akre Capital (Akre) | -27.6% | 1.08 | -0.03 | 0.42 | 0.67 | 299 |
| Harris Associates (Nygren) | -14.3% | 1.05 | 0.16 | 0.41 | 0.82 | 298 |
| Oaktree Capital (Marks) | 20.0% | 0.75 | 0.35 | 0.05 | 0.59 | 300 |
| Berkshire Hathaway (Buffett) | -7.8% | 1.07 | -0.10 | 0.49 | 0.78 | 298 |
| Duquesne FO (Druckenmiller) | 7.7% | 0.95 | 0.43 | -0.23 | 0.79 | 298 |
| Equal-weight (N=12) | 5.2% | 0.86 | 0.44 | -0.09 | 0.91 | 302 |
| Value-weight (N=12) | -8.5% | 1.04 | 0.01 | 0.40 | 0.86 | 302 |
| Consensus (>=2 of 12) | -2.6% | 1.00 | 0.25 | 0.00 | 0.89 | 302 |
| Consensus (>=3 of 12) | 0.1% | 1.08 | 0.30 | -0.44 | 0.85 | 302 |

## Notes

- Top-25 positions per filer are kept; smaller positions trimmed for tractability.
- ETF-proxy factors are correlated with but not identical to academic Fama-French. Loadings differ.
- α from SPY-only regression (left table) and 3-factor regression (right table) usually disagree; the 3-factor α is more conservative because SMB / HML absorb size and value tilts that single-factor α attributes to skill.
- Consensus strategies often hold cash heavily because mandate overlap is small; that's a real signal of mandate diversity.
- Yahoo v8 chart data is unofficial; treat differences smaller than ~3% alpha as noise.
