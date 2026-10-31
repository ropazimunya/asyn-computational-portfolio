# α-Synuclein Research | Computational Science, Quality & Risk Portfolio

**Structural bioinformatics · Scientific QA/QC · Data integrity · Risk-based decision-making · Regulatory reasoning**

## Project at a glance

This portfolio translates an exploratory **wild-type (WT) and A53T α-synuclein** computational research project into concrete examples of scientific analysis, research-record quality control, process improvement, risk assessment and regulatory-oriented scientific judgment. It separates **work performed on the historical research** from **software tests independently runnable here** and from **illustrative regulatory applications**.

The study examined predicted dimer interfaces, structural confidence, candidate interchain pockets, historical ligand-docking records and short molecular-dynamics workflows. The strongest independently runnable demonstration in this repository is a Python auditor tested with **synthetic** scientific records. This is a skills portfolio, **not a published clinical or experimental validation study**.

## Five professional competencies, with evidence

| Competency | Demonstration | Examine the work |
| --- | --- | --- |
| **Quality Assurance (QA)** | Requirements-to-test traceability, discrepancy investigation, corrective controls and regression verification | [B · Research QA & QC](portfolio/B_quality_assurance_control.md) |
| **Quality Control (QC)** | Programmatic checking of score, configuration, seed, version and file-inventory inconsistencies in synthetic records | [Runnable Python auditor](qa_auditor/README.md) |
| **Risk assessment & management** | Context-of-use-specific risk evaluation, control selection and residual-risk decisions for computational evidence | [D · Scientific risk management](portfolio/D_scientific_risk_management.md) |
| **Regulatory Affairs** | An illustrative research-to-regulated-use gap analysis: claims, intended use, evidence, traceability and change control | [E · Regulatory reasoning](portfolio/E_regulatory_affairs.md) |
| **Computational / research science** | WT/A53T predicted-interface comparisons, pocket-analysis approaches and molecular modeling workflow interpretation | [A · Structural bioinformatics](portfolio/A_structural_bioinformatics.md) · [C · Modeling & MD](portfolio/C_molecular_modeling.md) |

## Selected documented outcomes

- The historical ensemble analysis examined **five predicted structures per WT and A53T job**, including confidence, interchain contacts and model-selection sensitivity. Original prediction files remain private; its numerical results cannot be recomputed from this repository alone.
- The synthetic QA demonstration compares baseline and revised checks using **13 deliberately injected faults and one clean control**. The earlier baseline detected **9/13** faults and the revised checker detected **13/13**; see the included executable code, which generates its own reports when run.
- A reproducibility-focused interpretation distinguishes **record consistency** from **biological validity**: a log matching a configuration is necessary for traceability, not proof that docking establishes binding.
- A documented research risk assessment distinguishes uncertainty in structural models, simulation duration, evidence provenance and public-facing claims. The public case study presents the reasoning and representative controls, not the private corrective-action register.

## Explore the work

**A.** [Structural Bioinformatics](portfolio/A_structural_bioinformatics.md)
**B.** [Quality Assurance, Quality Control & Data Integrity](portfolio/B_quality_assurance_control.md)
**C.** [Molecular Modeling & Simulation](portfolio/C_molecular_modeling.md)
**D.** [Scientific Risk Management](portfolio/D_scientific_risk_management.md)
**E.** [Regulatory Affairs & Research Compliance](portfolio/E_regulatory_affairs.md)

**Run the evidence-backed software example:** [Python Scientific-Record Auditor](qa_auditor/README.md)
**Understand the evidence scope:** [Methods, reproducibility and limitations](docs/methods_and_evidence.md)

## Research integrity and interpretation

The structural models and putative pockets are computational hypotheses. **Predicted contacts do not establish a physiological dimer, docking scores do not prove experimental ligand binding, and short MD simulations do not demonstrate biological stabilization.** Internal laboratory/research records, restricted or unreviewed structural derivatives, and private audit materials are not included. FDA, GxP and other regulatory concepts are discussed as **skills-oriented analytical examples**, not as claims of formal project compliance, inspection, certification or regulatory submission.

## Scope and attribution

This repository contains a curated narrative and a synthetic-data Python example, not the complete historical molecular dataset. Scientific activities and interpretation were researcher-directed; some programming, debugging and drafting received AI assistance. No third-party structure files are redistributed, and no open-source software license is granted. Review ownership and reuse terms before any public visibility change.
