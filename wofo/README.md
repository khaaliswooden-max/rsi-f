# wofo

`wofo` is the Wooden Family Office agent toolkit. This subdirectory
holds wofo-specific code, data, and configuration. The rest of the
repo (the Zuup preference-collection app at the project root) is a
separate concern that lives alongside it for now.

## Layout

```
wofo/
├── thirteenf/        # SEC 13F-HR fetch / parse / analyze pipeline
│   ├── fetch.py      # EDGAR pull (requires WOFO_SEC_UA env var)
│   ├── parse.py      # XML → dataclasses
│   ├── analyze.py    # panel + qoq + concentration
│   └── cli.py        # `python -m wofo.thirteenf.cli {pull,analyze}`
├── prices/           # Pluggable price data sources
│   ├── source.py     # PriceSource protocol
│   ├── synthetic.py  # Deterministic random walk (tests / offline)
│   └── stooq.py      # Free Stooq daily-CSV adapter (prototyping)
├── research/         # Strategy generators
│   ├── follow_the_filer.py   # 13F panel → dated target weights
│   └── issuer_map.py         # Issuer name → ticker (heuristic + overrides)
├── backtest/         # Minimal portfolio backtester
│   ├── portfolio.py  # Target weights × prices → daily NAV
│   └── metrics.py    # CAGR / Sharpe / max drawdown
├── agent/            # Phase-1 (research-only) agent
│   ├── tools.py      # Read-only tools the agent may call
│   ├── runner.py     # Claude tool-use loop
│   └── demo_e2e.py   # Plumbing demo (no API key required)
└── data/
    └── 13f/
        ├── raw/      # one dir per quarter, primary_doc + infotable
        └── processed/  # JSON outputs + REPORT.md
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

The demo wires panel → follow-the-filer → synthetic backtest. Synthetic
prices are NOT real returns — this is a plumbing check.

```bash
python -m wofo.agent.demo_e2e
```

To run with real prices, swap `SyntheticPriceSource` for a real adapter:

```python
from wofo.prices.stooq import StooqPriceSource
src = StooqPriceSource()
```

Or implement your own adapter against the `wofo.prices.PriceSource`
protocol — Polygon, Tiingo, IBKR historical, etc.

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
