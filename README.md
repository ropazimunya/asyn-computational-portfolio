# Computational Research Quality and Scientific Evidence

[![Computational research portfolio validation](https://github.com/ropazimunya/asyn-computational-portfolio/actions/workflows/python-validation.yml/badge.svg)](https://github.com/ropazimunya/asyn-computational-portfolio/actions/workflows/python-validation.yml)

**Ropafadzo Zimunya | Independent research and professional portfolio**

This portfolio shows how I examine computational research records, investigate discrepancies, test quality controls and decide which conclusions the evidence can support. It draws on an exploratory WT/A53T α-synuclein project and includes a runnable Python demonstration using synthetic records.

The strongest public evidence is the executable QA workflow. The scientific archive also supports a documented investigation of docking records. Structural and molecular-dynamics activities are described with explicit source and verification boundaries. This work does not establish a validated cryptic pocket, ligand binding, therapeutic activity or regulated-system compliance.

## Interactive AlphaFold tutorial

[Open the interactive AlphaFold GFP tutorial](https://ropazimunya.github.io/asyn-computational-portfolio/alphafold-gfp-demo.html) to rotate public GFP structures, compare residue-level prediction confidence with experimental coverage, and explore predicted aligned error (PAE).

## Explore five competencies

| Case study | Work shown | Evidence |
| --- | --- | --- |
| [A · Structural bioinformatics](portfolio/A_structural_bioinformatics.md) | Model confidence, ensemble interpretation and selection sensitivity | Historical analysis records; no raw structures distributed |
| [B · QA, QC and data integrity](portfolio/B_quality_assurance_control.md) | Requirements, discrepancies, corrective controls and verification | Runnable tests, investigation and traceability matrix |
| [C · Molecular modeling](portfolio/C_molecular_modeling.md) | Docking record assessment and ligand-preparation investigation | Independently checked record agreement; historical investigation findings |
| [D · Scientific risk management](portfolio/D_scientific_risk_management.md) | Consequences, controls, residual uncertainty and disposition | Worked risk record linked to software evidence |
| [E · Regulatory affairs](portfolio/E_regulatory_affairs.md) | Intended use, claim strength and evidence gaps | Referenced educational assessment, not a submission |

## Start with the evidence

- [Completed investigation of docking-method discrepancies](quality/INVESTIGATION_001.md)
- [Claim-to-evidence matrix](evidence/CLAIM_EVIDENCE_MATRIX.csv)
- [Corrective-action record](quality/CORRECTIVE_ACTION_LOG.csv)
- [Scientific risk register](risk/SCIENTIFIC_RISK_REGISTER.csv)
- [Software validation results](qa_auditor/VALIDATION_REPORT.md)
- [Run the demonstration](qa_auditor/README.md)

## Selected results

The original synthetic comparison reproduces a baseline detection count of **9/13** and a revised count of **13/13**, with the clean control unflagged. These are designed examples, not field sensitivity estimates. Additional tests exercise malformed records, ZIP ambiguity and output-report integrity; exact results and open policy cases are recorded in the validation report.

A separate read-only comparison of supplied scientific records found **24/24** first-ranked docking log scores equal to their corresponding pose remarks and summary scores. This verifies agreement between records. It does not show that docking can be rerun identically or that the molecules bind.

## Evidence and authorship

This was researcher-directed independent work without a formal supervisor. AI assistance was used in coding, debugging, analysis support and documentation, including preparation of this portfolio. Findings have different verification levels; the [methods and limitations](docs/METHODS_AND_LIMITATIONS.md) and [source register](evidence/SOURCE_REGISTER.md) identify them.

Investigation and risk documents are retrospective portfolio records assembled from supplied evidence. They are not contemporaneous laboratory quality records or formal CAPA records from a regulated QMS. Scientific research files remain outside this public portfolio.

Python software is provided under the [MIT License](qa_auditor/LICENSE); prose, scientific interpretations and source-specific restrictions are described in [Content rights](CONTENT_RIGHTS.md). No FDA, institutional or third-party endorsement is claimed.
