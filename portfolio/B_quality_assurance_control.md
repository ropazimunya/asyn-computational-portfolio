# B Quality Assurance Quality Control and Data Integrity

## Quality objective

Check selected scientific records for completeness and internal consistency before using them in a methods narrative. The public demonstration uses synthetic Vina-style text, not molecular calculations.

| Requirement | Implemented control | Verification |
| --- | --- | --- |
| Required records are available | Cross-check ligand inventory, logs, poses and summary rows | Missing-record and orphan-result tests |
| Recognized fields are unambiguous | Identify labeled fields before full syntax validation | Malformed and repeated metadata tests |
| Selected scores agree | Compare first-ranked log, pose and summary values | Mismatch and rounding-boundary tests |
| Exceptions affect disposition | Link run-specific errors to run status | Invalid-secondary-pose test |
| Reports remain traceable | Source/member hashes and CSV/JSON consistency | Independent output assertions |

The historical baseline detects 9 of 13 planted faults. The revised checker detects all 13; the same clean control is unflagged. The baseline is preserved for educational comparison, not recommended as the operational checker.

## Worked investigation

[Investigation 001](../quality/INVESTIGATION_001.md) compares a manuscript's stated docking settings with the available execution records. A separate independent parser checks all 24 original first-ranked score records for internal agreement. No molecular docking is executed.

## Corrective controls and verification

Later testing identified malformed repeated fields, incorrect verified-run counting and script metadata that inferred too much from string matches. The current code rejects recognized malformed fields, excludes a run with a linked blocking exception from the verified count and labels script indicators as text occurrence only. [Validation results](../qa_auditor/VALIDATION_REPORT.md) give executed outcomes, including unresolved policy cases.

## Professional boundary

This demonstrates requirements mapping, QC checks, discrepancy investigation, corrective controls and verification. It is not a completed regulated CAPA, analytical-method validation or GMP qualification. The [corrective-action record](../quality/CORRECTIVE_ACTION_LOG.csv) keeps software verification separate from unresolved scientific provenance and molecular validity.
