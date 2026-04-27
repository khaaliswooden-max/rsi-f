# Eval run — rsi_default (rsi)

- Timestamp: 2026-04-27T14:31:19+00:00
- Git SHA: `n/a`
- Python: 3.11.15

## Summary

- **rubric_mean_fraction**: 0.3750
- **rubric_n**: 4
- **signal_mean_alpha_annual**: 0.0449
- **signal_mean_info_ratio**: 1.4054
- **signal_n**: 1

## Cases

### rubric:empty (rubric)

- judge: heuristic
- criteria_scores: {'provenance': 0, 'staleness_ack': 0, 'concrete_numbers': 0, 'fact_vs_opinion': 0, 'no_fabrication': 3, 'actionable': 0}
- total: 3
- max_total: 18
- score_fraction: 0.1667

### rubric:vague (rubric)

- judge: heuristic
- criteria_scores: {'provenance': 0, 'staleness_ack': 0, 'concrete_numbers': 0, 'fact_vs_opinion': 1, 'no_fabrication': 3, 'actionable': 2}
- total: 6
- max_total: 18
- score_fraction: 0.3333

### rubric:moderate (rubric)

- judge: heuristic
- criteria_scores: {'provenance': 0, 'staleness_ack': 0, 'concrete_numbers': 0, 'fact_vs_opinion': 1, 'no_fabrication': 3, 'actionable': 0}
- total: 4
- max_total: 18
- score_fraction: 0.2222

### rubric:strong (rubric)

- judge: heuristic
- criteria_scores: {'provenance': 3, 'staleness_ack': 3, 'concrete_numbers': 1, 'fact_vs_opinion': 2, 'no_fabrication': 3, 'actionable': 2}
- total: 14
- max_total: 18
- score_fraction: 0.7778

### signal:outperform_synthetic (signal)

- n_days: 200
- total_return_strategy: 0.3586
- total_return_benchmark: 0.3119
- cagr_strategy: 0.4979
- cagr_benchmark: 0.4305
- info_ratio: 1.4054
- alpha_annual: 0.0449
- beta: 0.9997
- r_squared: 0.9735
- up_capture: 1.0069
- down_capture: 0.9672
- max_drawdown_strategy: 0.1081
- max_drawdown_benchmark: 0.1166

