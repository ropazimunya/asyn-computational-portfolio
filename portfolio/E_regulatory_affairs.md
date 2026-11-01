# E Regulatory Affairs and Evidence Assessment

## Intended use before claims

This repository is educational research software and professional documentation. It is not offered for diagnosis, treatment selection or a medical-device submission. No FDA classification or pathway is asserted. A future regulated use would require its own product definition, intended use, applicable requirements and evidence plan.

## Worked claim assessment E01

**Proposed statement:** “The auditor validates molecular docking results.”

**Evidence:** synthetic files, selected field comparisons, designed fault detection and report checks. No real docking rerun, biological reference standard, binding experiment or clinical performance study is provided.

**Assessment:** the proposed statement exceeds the evidence. **Accepted statement:** “The auditor detects defined inconsistencies in documented synthetic Vina-style records.” **Traceability:** requirement Q02, risk R03, corrective action CA01 and the focused software tests. **Remaining gap:** real-format coverage and evidence authenticity are outside the current demonstration.

## Future regulated-use gap assessment

| Topic | Evidence here | Additional assessment for an actual regulated product |
| --- | --- | --- |
| Intended use | Educational consistency demonstration | Specific user, decision, product and setting |
| Requirements | Research-level schema and synthetic checks | Applicable product requirements and controlled traceability |
| Verification | Executed software regressions | Risk-appropriate verification for intended use |
| Validation | No biological or clinical validation | Relevant performance evidence for the actual claims |
| Records and change control | Retrospective portfolio records and source hashes | Applicable controlled processes and responsibilities |

FDA's 2023 computational-model credibility guidance addresses models used in medical-device submissions. Its context-of-use and risk-informed reasoning is useful educationally; it does not make this auditor FDA-validated or establish a device pathway. ICH Q9(R1) addresses pharmaceutical quality risk management and is likewise a reference, not a claimed compliance standard for this project.

[Official references](../docs/REFERENCES.md) · [Claim matrix](../evidence/CLAIM_EVIDENCE_MATRIX.csv) · [Scientific risk register](../risk/SCIENTIFIC_RISK_REGISTER.csv)
