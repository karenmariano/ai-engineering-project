# Evaluation Results

Evaluation uses the bundled synthetic policy corpus benchmarks in `data/corpus/benchmarks`.
The run disables live LLM calls so the metrics are reproducible under free-tier quota limits; answers are extractive from retrieved cited chunks.

## Summary

- Questions: 24
- Corpus chunks indexed: 135
- Groundedness: 100.0%
- Citation accuracy: 100.0%
- Top-1 retrieval hit rate: 87.5%
- Latency p50: 82.75 ms
- Latency p95: 89.66 ms

## Per-Question Results

| ID | Task | Expected Chunk | Top Citation | Citation Hit | Grounded | Latency ms |
| --- | --- | --- | --- | --- | --- | ---: |
| q001 | retrieval | `employee-handbook::4-attendance` | `employee-handbook::4-attendance` | True | True | 418.59 |
| q002 | retrieval | `code-of-conduct::5-gifts-and-hospitality` | `code-of-conduct::5-gifts-and-hospitality` | True | True | 90.35 |
| q003 | retrieval | `it-security-policy::7-incident-reporting` | `it-security-policy::7-incident-reporting` | True | True | 81.74 |
| q004 | retrieval | `data-protection-policy::5-retention` | `data-protection-policy::5-retention` | True | True | 82.35 |
| q005 | retrieval | `data-protection-policy::6-data-subject-requests` | `data-protection-policy::7-breach-response` | True | True | 84.31 |
| q006 | retrieval | `remote-work-policy::5-core-hours` | `remote-work-policy::5-core-hours` | True | True | 83.96 |
| q007 | retrieval | `leave-and-benefits-policy::3-annual-leave` | `leave-and-benefits-policy::3-annual-leave` | True | True | 82.21 |
| q008 | retrieval | `recruitment-and-onboarding-procedure::3-job-requisition` | `recruitment-and-onboarding-procedure::3-job-requisition` | True | True | 83.08 |
| q009 | retrieval | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 82.77 |
| q010 | retrieval | `performance-management-policy::5-rating-definitions` | `performance-management-policy::5-rating-definitions` | True | True | 83.16 |
| q011 | retrieval | `disciplinary-procedure::6-appeals` | `disciplinary-procedure::6-appeals` | True | True | 82.13 |
| q012 | retrieval | `finance-and-expense-policy::3-expense-categories` | `finance-and-expense-policy::3-expense-categories` | True | True | 85.62 |
| q013 | retrieval | `procurement-policy::4-three-quote-rule` | `procurement-policy::4-three-quote-rule` | True | True | 80.33 |
| q014 | retrieval | `risk-management-policy::4-risk-scoring` | `risk-management-policy::4-risk-scoring` | True | True | 80.69 |
| qa001 | qa | `employee-handbook::4-attendance` | `leave-and-benefits-policy::4-sick-leave` | True | True | 84.9 |
| qa002 | qa | `code-of-conduct::5-gifts-and-hospitality` | `code-of-conduct::5-gifts-and-hospitality` | True | True | 84.64 |
| qa003 | qa | `it-security-policy::5-password-and-mfa` | `it-security-policy::5-password-and-mfa` | True | True | 82.19 |
| qa004 | qa | `it-security-policy::7-incident-reporting` | `it-security-policy::7-incident-reporting` | True | True | 82.47 |
| qa005 | qa | `data-protection-policy::5-retention` | `data-protection-policy::5-retention` | True | True | 82.1 |
| qa006 | qa | `remote-work-policy::5-core-hours` | `remote-work-policy::5-core-hours` | True | True | 81.06 |
| qa007 | qa | `leave-and-benefits-policy::3-annual-leave` | `leave-and-benefits-policy::3-annual-leave` | True | True | 82.86 |
| qa008 | qa | `recruitment-and-onboarding-procedure::3-job-requisition` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 82.72 |
| qa009 | qa | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | `recruitment-and-onboarding-procedure::7-30-60-90-onboarding` | True | True | 81.75 |
| qa010 | qa | `risk-management-policy::4-risk-scoring` | `risk-management-policy::4-risk-scoring` | True | True | 85.72 |
