# Python scientific-record consistency demonstration

A research QA/QC proof-of-concept Python auditor for **synthetic Vina-style ZIP records**. The demonstration tests whether selected configuration, docking-log, pose-score, input-inventory and summary fields are consistent. It does **not** run molecular docking or analyze original biological outputs.

## Requirements
Python 3.9+; standard library only. Run the following commands from the repository root.

```bash
python3 qa_auditor/validation/compare_versions.py
python3 qa_auditor/tests/independent_tests.py qa_auditor/validation
python3 qa_auditor/tests/additional_hardening_tests.py
python3 qa_auditor/tests/reviewer_round4_tests.py
python3 qa_auditor/tests/reviewer_round5_tests.py
python3 qa_auditor/tests/reviewer_round6_tests.py
```

`python3` invokes the Python interpreter; each path identifies a synthetic test script. The independent test script also takes `qa_auditor/validation` as the location of the auditor modules. These scripts generate temporary synthetic inputs; some write generated reports under the same source tree. They should not be run on unpublished research data for this portfolio demo.

## Contents

- `validation/audit_workflow.py`: baseline logic.
- `validation/audit_workflow_v2.py`: updated consistency checks.
- `validation/compare_versions.py`: comparison of baseline and updated behavior using synthetic cases.
- `validation/validate_injected_faults.py`: synthetic fixture generation and test cases.
- `tests/`: independently structured regression and hardening scenarios.

## Professional quality-control connection

See [Chunk B](../portfolio/B_quality_assurance_control.md) for the requirements, corrective control, and test-evidence mapping behind this demonstration. The checks detect record inconsistencies within designed synthetic fixtures and do not constitute a regulated software-validation package.

## Scope
These scripts are specialized to a particular Vina-style ZIP naming convention and are not a general archival validation platform. Passing tests supports their behavior on defined synthetic cases only. It does not prove a predicted pocket, binding affinity or long-term stabilization.
