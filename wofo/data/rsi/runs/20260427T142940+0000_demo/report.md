# RSI loop report

- Started:  2026-04-27T14:29:40+00:00
- Finished: 2026-04-27T14:29:40+00:00
- Baseline summary: `{'rubric_mean_fraction': 0.375, 'rubric_n': 4, 'signal_mean_alpha_annual': 0.30828117635763136, 'signal_mean_info_ratio': 58440602578425.81, 'signal_n': 1}`

## Proposals

### rubric_concrete_numbers_tighter → **IMPROVE**

- Target: `wofo/evals/rubric.py`
- Proposer: `demo:good`
- Rationale: Reward each concrete figure (dollar amount, percent, share count) with one point instead of one-per-two. Lifts the score on quantitatively grounded notes without affecting empty / vague ones.
- rubric_mean_fraction: 0.3750 → 0.4028 (Δ +0.0278)
- Judge: rubric_mean_fraction +0.028; no metric regressed > 0.03

### rubric_provenance_broken → **REGRESS**

- Target: `wofo/evals/rubric.py`
- Proposer: `demo:bad`
- Rationale: Strawman: removes provenance scoring entirely. Should be flagged REGRESS by the judge.
- rubric_mean_fraction: 0.3750 → 0.3333 (Δ -0.0417)
- Judge: rubric_mean_fraction -0.042

### rubric_comment_only → **INCONCLUSIVE**

- Target: `wofo/evals/rubric.py`
- Proposer: `demo:neutral`
- Rationale: Comment-only change. Should produce no measurable eval delta.
- rubric_mean_fraction: 0.3750 → 0.3750 (Δ +0.0000)
- Judge: |delta| 0.000 below min_delta 0.02

## Disposition

Proposals labeled **IMPROVE** are candidates for human review and
merge. **REGRESS** and **INCONCLUSIVE** proposals should not be
merged but are kept on disk for failure analysis. **ERROR** proposals
indicate sandbox-execution problems and should be reproduced manually.
