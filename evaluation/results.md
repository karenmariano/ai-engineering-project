# Evaluation Results

Evaluation uses the bundled synthetic policy corpus benchmarks in `data/corpus/benchmarks`.
The run disables live LLM calls so the metrics are reproducible under free-tier quota limits; answers are extractive from retrieved cited chunks.

## Summary

- Questions: 24
- Corpus chunks indexed: 135
- Groundedness: 100.0%
- Citation accuracy: 100.0%
- Top-1 retrieval hit rate: 87.5%
- Latency p50: 82.26 ms
- Latency p95: 84.74 ms

## Per-Question Results

| ID | Task | Expected Chunk | Top Citation | Citation Hit | Grounded | Latency ms |
| --- | --- | --- | --- | --- | --- | ---: |
| q001 | retrieval | `employee-handbook::4-attendance` | `employee-handbook::4-attendance` | True | True | 195.05 |
| q002 | retrieval | `code-of-conduct::5-gifts-and-hospitality` | `code-of-conduct::5-gifts-and-hospitality` | True | True | 82.28 |
| q003 | retrieval | `it-security-policy::7-incident-reporting` | `it-security-policy::7-incident-reporting` | True | True | 83.0 |
| q004 | retrieval | `data-protection-policy::5-retention` | `data-protection-policy::5-retention` | True | True | 82.44 |
| q005 | retrieval | `data-protection-policy::6-data-subject-requests` | `data-protection-policy::7-breach-response` | True | True | 81.42 |
| q006 | retrieval | `remote-work-policy::5-core-hours` | `remote-work-policy::5-core-hours` | True | True | 82.71 |
| q007 | retrieval | `leave-and-benefits-policy::3-annual-leave` | `leave-and-benefits-policy::3-annual-leave` | True | True | 84.6 |
| q008 | retrieval | `recruitment-and-onboarding-procedure::3-job-requisition` | `recruitment-and-onboarding-procedure::3-job-requisition` | True | True | 84.45 |
| q009 | retrieval | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 81.62 |
| q010 | retrieval | `performance-management-policy::5-rating-definitions` | `performance-management-policy::5-rating-definitions` | True | True | 82.7 |
| q011 | retrieval | `disciplinary-procedure::6-appeals` | `disciplinary-procedure::6-appeals` | True | True | 81.39 |
| q012 | retrieval | `finance-and-expense-policy::3-expense-categories` | `finance-and-expense-policy::3-expense-categories` | True | True | 81.17 |
| q013 | retrieval | `procurement-policy::4-three-quote-rule` | `procurement-policy::4-three-quote-rule` | True | True | 81.96 |
| q014 | retrieval | `risk-management-policy::4-risk-scoring` | `risk-management-policy::4-risk-scoring` | True | True | 80.97 |
| qa001 | qa | `employee-handbook::4-attendance` | `leave-and-benefits-policy::4-sick-leave` | True | True | 81.23 |
| qa002 | qa | `code-of-conduct::5-gifts-and-hospitality` | `code-of-conduct::5-gifts-and-hospitality` | True | True | 82.46 |
| qa003 | qa | `it-security-policy::5-password-and-mfa` | `it-security-policy::5-password-and-mfa` | True | True | 83.51 |
| qa004 | qa | `it-security-policy::7-incident-reporting` | `it-security-policy::7-incident-reporting` | True | True | 82.24 |
| qa005 | qa | `data-protection-policy::5-retention` | `data-protection-policy::5-retention` | True | True | 81.15 |
| qa006 | qa | `remote-work-policy::5-core-hours` | `remote-work-policy::5-core-hours` | True | True | 80.65 |
| qa007 | qa | `leave-and-benefits-policy::3-annual-leave` | `leave-and-benefits-policy::3-annual-leave` | True | True | 81.71 |
| qa008 | qa | `recruitment-and-onboarding-procedure::3-job-requisition` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 84.76 |
| qa009 | qa | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 83.43 |
| qa010 | qa | `risk-management-policy::4-risk-scoring` | `risk-management-policy::4-risk-scoring` | True | True | 81.76 |
