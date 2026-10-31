# B | Quality Assurance, Quality Control & Data Integrity

**Target capability:** QA Associate, QC Analyst, Quality Systems Associate, Research Informatics.

## Problem and quality objective

Scientific results may be reported from records that disagree on settings, best scores, seeds, software versions or input inventories. The quality objective was to check **internal record consistency**, identify exception types and verify that software changes actually detect deliberately introduced faults.

## Requirements-to-evidence demonstration

| Quality requirement | Observable control in the Python demonstration | Evidence |
| --- | --- | --- |
| Records are complete | Identify missing log, pose or ligand-input items | [Auditor implementation](../qa_auditor/validation/audit_workflow_v2.py) |
| Critical metadata remain traceable | Compare seeds, software version and configuration fields | [Synthetic fault cases](../qa_auditor/validation/validate_injected_faults.py) |
| Scores are internally consistent | Compare score data among log, pose and summary records | [Version comparison](../qa_auditor/validation/compare_versions.py) |
| Quality changes are verified | Re-run baseline and updated controls against identical injected faults | [Test suite](../qa_auditor/README.md) |
| Exceptions are reported | Return discrete failed checks rather than quietly accepting mismatches | [Updated auditor](../qa_auditor/validation/audit_workflow_v2.py) |

## Demonstrated improvement: detect, correct, verify

**Observation:** In the original synthetic comparison, the baseline checker detected **9 of 13** deliberately injected faults. It missed defined seed/version/input-inventory scenarios.

**Corrective control:** The updated checker added checks addressing those gaps.

**Verification:** Re-running the same 13 faulty cases showed **13/13 detected**, while the clean control remained unflagged (**1/1**). The comparison script and tests are included and executable here. These numbers describe specific designed test cases, **not** a validated sensitivity estimate for real scientific archives.

## Professional QA/QC methods demonstrated

Requirements mapping, automated verification, exception classification, regression testing, test-evidence traceability, change verification and appropriate separation of factual observation from inference.

**Scope:** This is a *research software quality-control demonstration*. It is not evidence of completed GMP validation, formal CAPA closure under a regulated QMS, or certification of an analytical method. Historical docking consistency observations are omitted because source records are not in this public package.
