# wofo

`wofo` is the Wooden Family Office agent toolkit. This subdirectory
holds wofo-specific code, data, and configuration. The rest of the
repo (the Zuup preference-collection app at the project root) is a
separate concern that lives alongside it for now.

## Layout

```
wofo/
├── thirteenf/        # SEC 13F-HR fetch / parse / analyze pipeline
│   ├── fetch.py      # EDGAR pull via canonical submissions API
│   ├── parse.py      # XML → dataclasses
│   ├── analyze.py    # panel + qoq + concentration
│   └── cli.py        # `python -m wofo.thirteenf.cli {pull,analyze}`
├── prices/           # Pluggable price data sources
│   ├── source.py     # PriceSource protocol
│   ├── synthetic.py  # Deterministic random walk (tests / offline)
│   ├── stooq.py      # Stooq daily-CSV adapter (now requires apikey)
│   ├── yahoo.py      # Yahoo v8 chart adapter (free, unauthenticated)
│   └── cache.py      # Filesystem-cached PriceSource wrapper
├── research/         # Strategy generators
│   ├── follow_the_filer.py     # 13F panel → dated target weights
│   ├── issuer_map.py           # Issuer name → ticker (heuristic + overrides)
│   └── portfolio_of_filers.py  # Multi-manager combiners (eq / value / consensus)
├── backtest/         # Minimal portfolio backtester
│   ├── portfolio.py  # Target weights × prices → daily NAV
│   └── metrics.py    # CAGR / Sharpe / max drawdown
├── evals/            # Eval harness for the RSI loop
│   ├── signal.py     # Alpha / beta / info ratio / capture ratios
│   ├── rubric.py     # Rubric scoring (LLM judge + heuristic fallback)
│   └── registry.py   # Suite runner + versioned on-disk reports
├── agent/            # Phase-1 (research-only) agent
│   ├── tools.py            # Read-only tools the agent may call
│   ├── runner.py           # Claude tool-use loop
│   ├── demo_e2e.py         # Plumbing demo (synthetic prices)
│   ├── backtest_real.py    # SA LP backtest with cached Yahoo prices
│   └── multi_filer.py      # SA LP + Scion + Pabrai comparison
└── data/
    ├── 13f/
    │   ├── raw/         # SA LP filings (default location)
    │   ├── scion/raw/   # Scion Asset Management (Michael Burry)
    │   ├── pabrai/raw/  # Dalal Street LLC (Mohnish Pabrai)
    │   └── processed/   # JSON outputs + REPORT.md + MULTI_FILER_REPORT.md
    └── prices/          # Cached daily bars (CSV per ticker × window)
```

## Architecture, governance, and counsel

These are the documents to read first:

- [`docs/wofo-architecture.md`](../docs/wofo-architecture.md) — phased
  agent design, Phase 1 (research only) → Phase 2 (human-approved
  execution) → Phase 3 (bounded autonomous), and what
  "recursive self-improvement" actually means in this codebase.
- [`docs/family-office-counsel-packet.md`](../docs/family-office-counsel-packet.md)
  — intake doc to take to a securities lawyer + tax CPA. **This is
  not a filing and is not legal advice.** Wofo will not produce
  fileable legal documents.
- [`docs/repos.md`](../docs/repos.md) — survey of open-source building
  blocks (agents, EDGAR, market data, backtesting, evals, execution).

## Quick start: 13F pipeline

```bash
# 1. SEC requires identifying yourself.
export WOFO_SEC_UA="Wooden Family Office contact@yourdomain.com"

# 2. Pull all 13F filings for a manager (default example: Situational Awareness LP)
python -m wofo.thirteenf.cli pull --cik 0002045724

# 3. Parse + analyze the local raw/ tree.
python -m wofo.thirteenf.cli analyze
```

The analyze step prints a per-quarter summary and writes JSON +
`REPORT.md` to `wofo/data/13f/processed/`.

## Quick start: end-to-end strategy → backtest demo

Three demos, increasing in fidelity:

```bash
# 1. Plumbing check — synthetic prices, no network.
python -m wofo.agent.demo_e2e

# 2. Real prices — SA LP backtest vs SPY using cached Yahoo daily bars.
python -m wofo.agent.backtest_real

# 3. Multi-filer comparison — SA LP + Scion + Pabrai, plus three
#    portfolio-of-filers combinations (equal, value, consensus).
python -m wofo.agent.multi_filer
```

The `wofo/data/prices/` directory is checked in for reproducibility.
Delete it and re-run to refresh from Yahoo. To swap in a paid feed,
implement the `wofo.prices.PriceSource` protocol — see
`wofo/prices/yahoo.py` for a reference.

## Multi-filer findings (so far)

The latest `multi_filer.py` run produces something like:

| Strategy | Total ret | Sharpe | MaxDD | α (annual) | β |
|---|---:|---:|---:|---:|---:|
| SA LP solo | 94.5% | 1.45 | 35.7% | 42.5% | 1.63 |
| Scion solo | -5.2% | -0.04 | 26.3% | -9.3% | 0.54 |
| Pabrai solo | 52.0% | 1.10 | 26.2% | 34.9% | 0.52 |
| Equal-weight 3 | 51.9% | **1.43** | **21.3%** | 25.3% | 0.90 |
| Value-weight 3 | 61.4% | 1.31 | 29.2% | 29.1% | 1.17 |
| Consensus (≥2) | -2.9% | -0.09 | 10.7% | -3.4% | 0.14 |

Key observation: equal-weighting three orthogonal mandates produces
roughly the same Sharpe as the best single manager with materially
lower drawdown. Consensus is mostly empty because the mandates don't
overlap — a real signal, not a bug.

## Quick start: agent loop (Phase 1, research only)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...

python - <<'PY'
from wofo.agent import run_research_loop
out = run_research_loop(
    "Summarize Situational Awareness LP's Q4 2025 portfolio "
    "and the largest position changes from Q3 to Q4."
)
print(out["final_text"])
PY
```

The agent has access only to read-only research tools
(`list_local_filings`, `summarize_panel`, `top_holdings`,
`qoq_activity`). It cannot place orders, transfer funds, or modify any
account. See `wofo/agent/tools.py` for the tool schemas.

## Tests

```bash
python -m pytest
```

All tests run against committed sample data (no network required).

## What `wofo` will not do

- File legal or tax documents on your behalf.
- Trade real capital before counsel sign-off and a paper-trade track
  record (see `docs/wofo-architecture.md`, Phase 1 → Phase 2 gate).
- Modify and redeploy its own production code unattended.
- Accept outside investment, market itself, or hold itself out as an
  adviser to non-family clients (would void the SEC Family Office Rule
  exemption — see counsel packet).
