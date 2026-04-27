# wofo

`wofo` is the Wooden Family Office agent toolkit. This subdirectory
holds wofo-specific code, data, and configuration. The rest of the
repo (the Zuup preference-collection app at the project root) is a
separate concern that lives alongside it for now.

## Layout

```
wofo/
├── thirteenf/        # SEC 13F-HR fetch / parse / analyze pipeline
├── prices/           # Pluggable price sources (Yahoo, Stooq, synthetic, cache)
├── factors/          # Factor models (ETF-proxy, synthetic) for performance attribution
├── research/         # Strategy generators
│   ├── follow_the_filer.py     # 13F panel → dated target weights
│   ├── issuer_map.py           # Issuer name → ticker (heuristic + overrides)
│   ├── overrides.py            # Curated CUSIP / issuer → ticker overrides
│   └── portfolio_of_filers.py  # Multi-manager combiners (eq / value / consensus)
├── backtest/         # Minimal portfolio backtester (no numpy dep)
├── evals/            # Eval harness — signal evals, rubric, factor decomp
├── rsi/              # Recursive self-improvement loop
│   ├── proposal.py         # Proposal + Outcome dataclasses
│   ├── proposers.py        # Mock / file / Anthropic proposers
│   ├── sandbox.py          # Apply proposal in tmp tree + run eval
│   ├── judge.py            # IMPROVE / REGRESS / INCONCLUSIVE classifier
│   ├── loop.py             # Orchestrator + on-disk artifacts
│   ├── eval_runner.py      # Default eval suite for the loop
│   ├── demo_proposals.py   # Three canned proposals (good / bad / neutral)
│   └── cli.py              # `python -m wofo.rsi.cli {demo,file <path>}`
├── agent/            # Phase-1 (research-only) agent + demo runners
│   ├── tools.py            # Read-only tools the agent may call
│   ├── runner.py           # Claude tool-use loop
│   ├── demo_e2e.py         # Plumbing demo (synthetic prices)
│   ├── backtest_real.py    # SA LP backtest with cached Yahoo prices
│   ├── multi_filer.py      # 3-filer comparison (SA LP + Scion + Pabrai)
│   └── multi_filer_n.py    # N=12 comparison + 3-factor decomposition
└── data/
    ├── 13f/{salp,scion,pabrai,baupost,...}/raw  # 13F filings per manager
    ├── prices/                                  # Cached daily bars (Yahoo)
    ├── evals/runs/                              # Versioned eval-suite outputs
    └── rsi/runs/                                # Versioned RSI loop reports
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

## Multi-filer findings

`multi_filer_n.py` runs the full N=12 roster (SA LP + Scion + Pabrai +
Baupost + Pershing + Appaloosa + Third Point + Akre + Harris + Oaktree
+ Berkshire + Duquesne) over Feb 2025 → Apr 2026.

Top of the table (Sharpe-ranked):

| Strategy | Total | Sharpe | MaxDD | SPY α | β | 3-factor α |
|---|---:|---:|---:|---:|---:|---:|
| Oaktree (Marks) | 45.8% | **1.75** | 17.0% | 21.6% | 0.75 | 20.0% |
| Situational Awareness LP | 113.1% | 1.43 | 46.0% | 47.0% | 2.15 | 51.0% |
| Baupost (Klarman) | 30.6% | 1.34 | **14.2%** | 12.6% | 0.76 | 9.1% |
| Pabrai | 51.6% | 1.10 | 26.2% | 34.7% | 0.52 | 29.9% |
| Equal-weight (N=12) | 24.7% | 1.07 | 19.4% | 5.8% | 0.92 | 5.2% |
| Duquesne (Druckenmiller) | 28.6% | 1.03 | 23.2% | 7.8% | 1.08 | 7.7% |

Two important observations from the 3-factor decomposition:

1. **3-factor α is more conservative than SPY-only α** — SMB and HML
   absorb size and value tilts that single-factor regressions
   attribute to "skill." E.g. Pabrai's 35% SPY α drops to 30% once you
   account for his small-cap-value loading. SA LP's 47% SPY α is
   actually mostly small-cap-growth beta (β_smb 1.54, β_hml -1.54).
2. **Equal-weight (N=12) loses most of the alpha** but keeps Sharpe
   high (1.07) at 19.4% drawdown. The diversification benefit is real,
   but the cost is that you're averaging skill with non-skill — a
   curated subset (top-Sharpe filers only) might dominate; that's the
   next experiment.

Full report: `wofo/data/13f/processed/MULTI_FILER_N_REPORT.md`.

## RSI (recursive self-improvement) loop

The agent proposes diffs to its own code; the loop applies each diff
in a sandbox, runs the eval suite, and classifies the change as
**IMPROVE**, **REGRESS**, or **INCONCLUSIVE**. Humans review and merge.

```bash
# Demo with three canned proposals (one good, one bad, one neutral)
python -m wofo.rsi.cli demo

# Run from a JSON file the agent (or a human) wrote earlier
python -m wofo.rsi.cli file path/to/proposals.json
```

Reports land in `wofo/data/rsi/runs/{ts}_{label}/report.md`. The loop
never writes to `main` and never auto-merges anything. See
`docs/wofo-architecture.md` for why this is the bar.

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
