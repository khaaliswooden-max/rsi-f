# Repository survey — building blocks for `wofo`

Curated list of open-source projects that map onto wofo's needs. Each
entry includes the role it would play and the main tradeoff. Stars and
activity below are directional — verify before adopting.

## A. Agent / orchestration layer

| Project | Role | Tradeoff |
|---|---|---|
| **Claude Agent SDK** (`@anthropic-ai/claude-agent-sdk`) | Build the wofo agent itself — tool use, sub-agents, file/bash tools out of the box. | Anthropic-first; pairs naturally with this repo's existing Claude usage but couples you to one model vendor. |
| **LangGraph** (langchain-ai/langgraph) | State-machine orchestration for multi-step agents; good for the "research → propose → review" loop. | Heavy abstraction surface; can obscure what the agent is actually doing if you're not careful. |
| **OpenAI Agents SDK** | Alternative agent runtime. | Vendor lock-in to OpenAI; useful as a comparison baseline for evals. |
| **smolagents** (huggingface/smolagents) | Minimal Python agent framework, code-execution focus. | Small surface, easy to reason about; less mature than the bigger frameworks. |

**Recommendation for wofo:** start with the Claude Agent SDK as the
primary runtime since this repo is already Claude-centric, and keep
the prompt + tool definitions vendor-neutral so swapping is feasible.

## B. SEC / fundamental data

| Project | Role | Tradeoff |
|---|---|---|
| **sec-edgar-downloader** (jadchaar/sec-edgar-downloader) | Pull EDGAR filings by CIK / form. | Convenience over the raw HTTP we currently use; adds a dependency we may not need given how small `wofo/thirteenf/fetch.py` already is. |
| **edgartools** (dgunning/edgartools) | High-level Pythonic EDGAR with fund / 13F helpers. | Good for prototyping; verify license + the way it caches data fits your compliance posture. |
| **python-edgar** (jzhao-jam/python-edgar) | Lightweight EDGAR index parser. | Older, narrower; fine if you only need filing indexes. |
| **openbb** (OpenBB-finance/OpenBB) | Aggregator across many free + paid data sources. | Useful as a one-stop shop for prototyping; the operational dependency surface is large. |

**Recommendation:** keep our own thin EDGAR fetcher (already written;
no extra dep). Add `edgartools` only if we need filings beyond 13F that
would be tedious to parse from scratch (e.g., 8-K item parsing).

## C. Market data

| Project | Role | Tradeoff |
|---|---|---|
| **yfinance** | Free OHLCV via Yahoo. | Unofficial, rate-limited, breaks periodically; fine for backtesting prototypes, **not** for production. |
| **Alpaca Markets API** | Free-tier US equities historical + live; paper trading. | Good Phase-1 → Phase-2 ramp; quality of data is OK but not institutional. |
| **Polygon.io** | Paid, institutional-grade equities/options. | Costs real money; the right move once strategies justify it. |
| **Tiingo / EOD Historical** | Paid historical fundamentals + prices. | Comparison-shop. |

**Recommendation:** prototype on Alpaca paper-trading (free) for
Phases 1–2; budget for Polygon when there's a strategy worth paying
for.

## D. Backtesting

| Project | Role | Tradeoff |
|---|---|---|
| **vectorbt** (polakowo/vectorbt) | Vectorized backtesting; very fast for parameter sweeps. | Steep learning curve; the API rewards careful reading. |
| **backtrader** | Event-driven backtester, mature ecosystem. | Slower than vectorbt for sweeps; clearer semantics for path-dependent strategies. |
| **zipline-reloaded** | Quantopian-era event-driven engine. | Solid but heavyweight setup; data ingestion is a project of its own. |
| **bt** (pmorissette/bt) | Portfolio-level backtester, clean API. | Less feature-rich than vectorbt; great for "what would this allocation have done" questions. |

**Recommendation:** start with **bt** for portfolio-level questions
(matches the 13F-following use case naturally); add **vectorbt** if /
when we need parameter sweeps over signal rules.

## E. Eval / RSI loop

| Project | Role | Tradeoff |
|---|---|---|
| **inspect-ai** (UKAISI/inspect_ai) | Eval framework for LLM agents; good for the "score wofo against itself over time" loop. | Designed for safety evals; bend it to investment-research evals carefully. |
| **promptfoo** | Prompt regression testing; CI-friendly. | More about prompt tuning than agent behavior. |
| **OpenAI evals / lm-eval-harness** | General LLM benchmarks. | Mostly capability evals; less directly useful here, but worth knowing for sanity checks. |

**Recommendation:** build a small bespoke eval harness in
`wofo/evals/` (research-quality rubric scored by a judge model + signal
backtest delta), and import patterns from `inspect-ai` rather than
adopting it wholesale.

## F. Execution (Phase 2+ only)

| Project | Role | Tradeoff |
|---|---|---|
| **alpaca-py** | Official Alpaca SDK; supports paper + live. | US equities + crypto only; fine for a starting point. |
| **ib_insync** | Pythonic wrapper over Interactive Brokers TWS API. | IBKR is the institutional standard; setup pain is real but capabilities are deep. |
| **ccxt** | Crypto exchange aggregator. | **Out of scope per architecture doc** until custody review is done. |

**Recommendation:** Phase 2 entry point is Alpaca paper. Phase 3 entry
point is IBKR via `ib_insync` once counsel and ops are ready.

## G. Governance / ops

| Project | Role | Tradeoff |
|---|---|---|
| **DVC** | Version control for data + models. | Useful once we accumulate enough non-text artifacts (models, large parquet files); overkill at the current scale. |
| **MLflow** | Experiment tracking. | Heavy for our current usage; revisit at Phase 2. |
| **DuckDB** | Embedded analytics SQL over parquet/CSV. | Cheap and great for the kind of panel analysis we do today; recommend adopting for `wofo/data/`. |

**Recommendation:** add **DuckDB** as the standard query layer for the
data we accumulate. Defer DVC / MLflow until they earn their keep.

## What we have decided to *not* use

- **Auto-GPT / BabyAGI–style "fully autonomous" frameworks.** Mismatch
  with the human-gated review model in `docs/wofo-architecture.md`.
- **Any "AI trader" / "GPT alpha" SaaS.** Black-box model + black-box
  data + opaque execution = unauditable. Nope.
- **Anything that requires sending account credentials or PII to a
  third-party hosted service** outside vetted custodians.
