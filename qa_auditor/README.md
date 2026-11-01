# Scientific Record Consistency Demonstration

Python 3.9+ and the standard library are required. The tested runtime is recorded in the [validation report](VALIDATION_REPORT.md). No Vina, OpenMM, molecular data or network access is needed.

## Run all verification

From the repository root:

```bash
python3 tools/run_validation.py
```

`python3` starts Python. `tools/run_validation.py` runs the supplied suites and focused report-integrity tests, records actual exit statuses and writes a generated execution summary under qa_auditor/generated. It returns nonzero if an asserted expectation fails. Three historical cases remain REVIEW and are reported separately, not converted into passes.

## Audit a compatible synthetic archive

```bash
python3 qa_auditor/validation/audit_workflow_v2.py example.zip audit_output --expected-version 1.2.7
```

`python3` invokes Python. The script path selects the revised auditor; `example.zip` is the input archive; `audit_output` is a new report directory; `--expected-version 1.2.7` sets the comparison version. The command checks records without performing docking. Exit 1 requests inspection of recorded discrepancies or review flags.

[Input layout, policies and limitations](INPUT_SPECIFICATION.md) · [Case B](../portfolio/B_quality_assurance_control.md)

## Historical baseline

validation/audit_workflow.py and validate_injected_faults.py preserve the weaker baseline demonstration. Running the baseline-only harness returns 1 because it misses four of the thirteen planted faults. This expected historical result is not failure of the revised auditor. The baseline must not be used as the recommended checker.

The tests with review-round names retain historical regression lineage. They are bundled software tests, not institutional approval or independent scientific validation. Several share fixture code; their scenario counts overlap.
