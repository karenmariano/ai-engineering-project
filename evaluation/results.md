# Evaluation Results

Evaluation uses the bundled synthetic policy corpus benchmarks in `data/corpus/benchmarks`.
The run disables live LLM calls so the metrics are reproducible under free-tier quota limits; answers are extractive from retrieved cited chunks.

## Summary

- Questions: 24
- Corpus chunks indexed: 135
- Groundedness: 100.0%
- Citation accuracy: 100.0%
- Top-1 retrieval hit rate: 87.5%
- Latency p50: 7.5 ms
- Latency p95: 10.15 ms

## Per-Question Results

| ID | Task | Expected Chunk | Top Citation | Citation Hit | Grounded | Latency ms |
| --- | --- | --- | --- | --- | --- | ---: |
| q001 | retrieval | `employee-handbook::4-attendance` | `employee-handbook::4-attendance` | True | True | 7511.73 |
| q002 | retrieval | `code-of-conduct::5-gifts-and-hospitality` | `code-of-conduct::5-gifts-and-hospitality` | True | True | 10.39 |
| q003 | retrieval | `it-security-policy::7-incident-reporting` | `it-security-policy::7-incident-reporting` | True | True | 7.43 |
| q004 | retrieval | `data-protection-policy::5-retention` | `data-protection-policy::5-retention` | True | True | 7.71 |
| q005 | retrieval | `data-protection-policy::6-data-subject-requests` | `data-protection-policy::7-breach-response` | True | True | 7.99 |
| q006 | retrieval | `remote-work-policy::5-core-hours` | `remote-work-policy::5-core-hours` | True | True | 7.82 |
| q007 | retrieval | `leave-and-benefits-policy::3-annual-leave` | `leave-and-benefits-policy::3-annual-leave` | True | True | 7.68 |
| q008 | retrieval | `recruitment-and-onboarding-procedure::3-job-requisition` | `recruitment-and-onboarding-procedure::3-job-requisition` | True | True | 7.8 |
| q009 | retrieval | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 6.86 |
| q010 | retrieval | `performance-management-policy::5-rating-definitions` | `performance-management-policy::5-rating-definitions` | True | True | 8.06 |
| q011 | retrieval | `disciplinary-procedure::6-appeals` | `disciplinary-procedure::6-appeals` | True | True | 7.4 |
| q012 | retrieval | `finance-and-expense-policy::3-expense-categories` | `finance-and-expense-policy::3-expense-categories` | True | True | 7.57 |
| q013 | retrieval | `procurement-policy::4-three-quote-rule` | `procurement-policy::4-three-quote-rule` | True | True | 8.71 |
| q014 | retrieval | `risk-management-policy::4-risk-scoring` | `risk-management-policy::4-risk-scoring` | True | True | 8.06 |
| qa001 | qa | `employee-handbook::4-attendance` | `leave-and-benefits-policy::4-sick-leave` | True | True | 8.76 |
| qa002 | qa | `code-of-conduct::5-gifts-and-hospitality` | `code-of-conduct::5-gifts-and-hospitality` | True | True | 7.11 |
| qa003 | qa | `it-security-policy::5-password-and-mfa` | `it-security-policy::5-password-and-mfa` | True | True | 7.27 |
| qa004 | qa | `it-security-policy::7-incident-reporting` | `it-security-policy::7-incident-reporting` | True | True | 6.67 |
| qa005 | qa | `data-protection-policy::5-retention` | `data-protection-policy::5-retention` | True | True | 7.03 |
| qa006 | qa | `remote-work-policy::5-core-hours` | `remote-work-policy::5-core-hours` | True | True | 6.38 |
| qa007 | qa | `leave-and-benefits-policy::3-annual-leave` | `leave-and-benefits-policy::3-annual-leave` | True | True | 6.8 |
| qa008 | qa | `recruitment-and-onboarding-procedure::3-job-requisition` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 7.13 |
| qa009 | qa | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 6.96 |
| qa010 | qa | `risk-management-policy::4-risk-scoring` | `risk-management-policy::4-risk-scoring` | True | True | 6.94 |
