# Software Validation Evidence

**Edition 1.0. Execution environment:** Linux, Python 3.12.14, standard library only. This record describes completed software verification for the stated synthetic scope. It is not regulated validation, independent biological confirmation or third-party certification.

## Executed results

| Suite | Exit | Observed result |
| --- | ---: | --- |
| Original comparison | 0 | 14/14 expectations; baseline 9/13 faults, revised 13/13; clean control unflagged |
| Historical independent fixtures | 0 | 26 PASS, 3 REVIEW, 0 FAIL |
| Hardening | 0 | 10/10 |
| Round four | 0 | 7/7 |
| Round five | 0 | 3/3 |
| Round six | 0 | 5/5 |
| Focused portfolio integrity | 0 | 13/13 |

These counts overlap and do not represent unique independent experiments. The historical independent fixtures originated in earlier review work; bundling and extending them here is regression testing. Current execution and documentation used AI assistance.

## What was asserted

The runner reads generated comparison CSV/JSON, verifies the advertised baseline/revised counts and checks the exact REVIEW set. Focused tests invoke the actual CLI and assert exit status, issue category, all four reports, exception-list equality between CSV and JSON, run-specific FAIL disposition, verified totals, archive hashes and every manifest-member hash. A distinct fixture generator uses different grid values, scores, seeds and ligand identifiers from the historical suite.

Malformed repeated score, version, exhaustiveness and seed records now fail. A malformed secondary pose remark prevents its WT run from being counted as verified. Script metadata is explicitly text occurrence, including comment text. Empty ligand content is accepted under the documented presence-only scope; this is an asserted limitation, not molecular validation.

## Three explicit REVIEW outcomes

| ID | Observation | Interpretation |
| --- | --- | --- |
| C7 | ALERT(6) for version 1.2.5 under expected 1.2.7 | Pinned-version policy; another legitimate version requires deliberate selection |
| F18 | SILENT after consistent changes to log, pose and summary | Known authenticity limitation of consistency checks |
| C9 | ALERT(2) for one-decimal log versus a more precise pose/summary | Real-log rounding policy remains unvalidated |

They are not counted as passes. A zero suite exit means configured assertions passed, not that these questions disappeared.

## Retained evidence and reproduction

[Execution summary](../evidence/validation/execution_summary.json) · [Focused case results](../evidence/validation/portfolio_integrity_results.json) · [Comparison rows](../evidence/validation/v1_vs_v2_fault_detection.csv)

Suite stdout is retained in the same evidence directory. Running the verification command in the software README generates a fresh execution record under qa_auditor/generated without overwriting the retained snapshot. The baseline-only suite intentionally returns 1 when demonstrating its four missed faults.

Windows, macOS, Python 3.9 execution and actual GitHub Actions outcomes were not observed in this edition. A CI workflow is included to run them. No network, docking, MD or clinical test was executed by the synthetic suites. Archive resource controls are safeguards, not adversarial security certification.
