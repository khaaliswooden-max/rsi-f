# wofo — Architecture

`wofo` (Wooden Family Office agent) is the working name for the AI agent
that supports research and (eventually) execution for the Wooden Family
Office. This document describes the phased design.

The two non-negotiable design constraints:

1. **No real capital is at risk until counsel signs off on the regulatory
   posture and an out-of-sample track record exists on paper.**
2. **Self-modification is gated by humans until the agent has demonstrated
   it can reliably propose safe, narrow changes.** "Recursive
   self-improvement" here means an iterative loop of *proposed* diffs
   evaluated against an eval suite, not unattended deployment.

## Phases

### Phase 1 — Research & signal generation (no capital)

Goal: produce reproducible, dated research artifacts and paper-traded
signals.

Capabilities:
- Pull primary-source filings (13F, 13D/G, 4, S-1, 8-K) from SEC EDGAR.
- Pull alt data the family chooses to license or ingest.
- Generate ranked watchlists with explicit thesis text and provenance.
- Backtest signal rules against historical price data.
- Produce a weekly research digest the principal reads.

Tech surface:
- `wofo/thirteenf/` — implemented. EDGAR pull, parse, panel analytics.
- `wofo/research/` — to add. Notebook + report generators.
- `wofo/backtest/` — to add. Wraps a vetted backtester (see
  `docs/repos.md` for shortlist).
- `wofo/agent/` — to add. The orchestration layer that drives a
  Claude-based agent through research tasks.

Success criteria to exit Phase 1:
- ≥4 quarters of paper-traded signals logged with timestamps before any
  hindsight-aware decisions.
- Risk-adjusted return (Sharpe, max drawdown, hit rate) measured against
  a benchmark (SPY, QQQ, sector-matched).
- Independent review of the strategy by a person who is not the agent
  author.

### Phase 2 — Human-in-the-loop execution

Goal: the agent proposes orders; a human approves each one before it
hits the wire.

New capabilities:
- Broker integration via a vetted, auditable API (likely Interactive
  Brokers TWS or Alpaca for equities; nothing exotic).
- Order-staging UI with the agent's rationale, position-size
  justification, and risk metrics shown alongside the proposed ticket.
- Append-only audit log of (proposal, decision, fill).

Pre-flight checklist before flipping Phase 2 on:
- [ ] Counsel sign-off on adviser posture (see counsel packet).
- [ ] Prime brokerage / custody account set up for the management entity.
- [ ] Insurance reviewed (E&O, D&O if applicable).
- [ ] Kill-switch tested.
- [ ] Position size limits, single-name limits, and sector limits hard-coded.

### Phase 3 — Bounded autonomous execution

Goal: agent executes within a tight sandbox without per-order approval.

This is **only** considered if Phases 1 and 2 produced a track record
that justifies it, and only with hard guardrails:
- Per-trade notional cap.
- Daily notional / VaR cap.
- Whitelist of instruments (no options, no leverage, no short-side until
  separately approved).
- Mandatory stop on N consecutive losses or X% drawdown.
- Counsel review of the autonomy scope.

## "Recursive self-improvement" — what it means here

We are *not* building an agent that rewrites and redeploys its own
production code unattended. That is not the bar that any reasonable
review would clear, and it is not what the family office actually needs.

What we *are* building:

1. An **eval harness** the agent runs against itself: backtests,
   research-quality rubrics scored by a separate judge model, code-review
   bots over its own diffs.
2. A **proposal loop**: the agent proposes diffs to its own prompts,
   tools, and rules, and submits them as PRs against this repo.
3. **Human merge gate**: the principal (or a delegate) reviews and
   merges. The agent never has write access to `main`.
4. **Versioned rollback**: every prompt / tool / rule change is a
   commit with an attached eval delta.

This gives the loop the *shape* of recursive self-improvement (the
agent gets measurably better over time by editing itself) without the
risk profile of an autonomous deployer.

## "Self-financing" — what it means here

The agent generates the operating cash for the Wooden Family Office by
producing investment research and (Phase 2+) executing trades within
the family office vehicle. The agent does not take fees, does not have
external clients, and does not market itself — those would all change
the regulatory posture materially.

## Out of scope (explicitly)

- Crypto trading on permissionless venues without custody review.
- Any leverage product (options, futures, margin) until separately
  approved.
- Counterparty exposure outside vetted brokers/custodians.
- Acting on material non-public information from any source.
- Touching client funds or accepting outside investment of any kind
  (that would void the SEC Family Office Rule exemption — see counsel
  packet).
