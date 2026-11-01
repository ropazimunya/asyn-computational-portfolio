# D Scientific Risk Assessment and Risk Management

## Context of use

Decide what a public research portfolio may credibly communicate. This is a retrospective educational scientific-risk assessment, not patient-safety analysis, ISO 14971 implementation or a pharmaceutical QMS assessment.

## Worked risk R03

**Failure mode:** a malformed repeated execution field is ignored and a record appears acceptable. **Consequence:** incorrect settings or an ambiguous score may be repeated in a methods narrative. **Initial priority:** high, because it directly affects record interpretation and had a demonstrated software escape. Priorities are qualitative screening judgments; no numeric failure probability is assigned.

**Control:** identify all recognized occurrences, reject malformed or repeated fields, and persist the exception. **Verification:** the focused portfolio tests mutate score, version, exhaustiveness and seed records and assert nonzero CLI status, expected issue category, CSV/JSON agreement and affected-run disposition. Exact outcomes are in the [validation report](../qa_auditor/VALIDATION_REPORT.md).

**Residual risk:** synchronized changes across all record sources can still pass a consistency check. Hashes identify the submitted bytes but cannot prove original execution or prevent coordinated fabrication. **Disposition:** acceptable for a narrowly described synthetic consistency demonstration; unsuitable as proof of biological validity or comprehensive provenance.

## Control decisions across the project

| Risk | Control | Disposition |
| --- | --- | --- |
| Model-selection dependence | Ensemble interpretation and sensitivity disclosure | Historical observation; no stability claim |
| Methods versus execution mismatch | Record comparison and explicit investigation | Conflicting methods are not carried forward as verified |
| Ligand mapping error | Withhold original MD stability interpretation | Scientific validity remains unresolved |
| Software overclaims | Defect-specific regression checks and report assertions | Tested behavior only |
| Source-use restrictions | Keep molecular artifacts outside public package | No legal clearance inferred from omission |

The [risk register](../risk/SCIENTIFIC_RISK_REGISTER.csv) identifies evidence, control, status and residual uncertainty. Software control verification is completed for the tested fixtures; molecular provenance and generalization to real archives remain separate limitations.

## Reference framework

ICH Q9(R1) provides pharmaceutical quality-risk-management principles. It informs this educational emphasis on context, uncertainty and controls; this portfolio does not claim implementation of that guidance. [Reference](../docs/REFERENCES.md)
