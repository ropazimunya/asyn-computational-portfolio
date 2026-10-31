# α-Synuclein Dimer Interfaces | Computational Research Portfolio

**Structural bioinformatics · Molecular modeling · Python · Scientific data quality**

## Research overview

This portfolio presents an exploratory computational study of **wild-type (WT)** and **A53T α-synuclein** dimer-interface models. The work investigates how predicted interfaces vary across models, how candidate interchain pockets can be examined, and how research code can improve the traceability of docking records.

The project connects structural prediction, model-confidence assessment, interface and pocket geometry, historical molecular docking, molecular-dynamics workflow documentation, and a **reproducible synthetic-data validation example**. It is computational, hypothesis-generating work, not experimental verification of a stable dimer or therapeutic ligand.

## Research questions

1. How do selected WT and A53T predicted dimer models differ in interface confidence and contact geometry?
2. How sensitive are candidate interchain pocket descriptions to model selection and structural preparation?
3. How can Python checks detect inconsistent computational records before interpretation?

## Project work

| Area | Methods | Portfolio evidence |
| --- | --- | --- |
| Structural bioinformatics | Predicted-dimer confidence and interface comparisons | [Model and interface analysis](portfolio/structural_bioinformatics.md) |
| Candidate pocket investigation | Contact maps, ensemble variation, pocket geometry | [Pocket analysis](portfolio/pocket_analysis.md) |
| Docking and MD workflow | AutoDock Vina records and OpenMM workflow documentation | [Molecular modeling](portfolio/molecular_modeling.md) |
| Scientific programming | Python, synthetic fault injection, test cases | [Runnable data-quality demo](qa_auditor/README.md) |

## Reproducible demonstration

The included Python auditor uses **synthetic Vina-style scientific records** to test format and consistency checks. It does **not** need original protein structures, docking outputs or molecular trajectories. It demonstrates test design, validation logic, error handling and results comparison, but does not reproduce the original molecular screening study.

See [QA/QC software demonstration](qa_auditor/README.md) for requirements and test commands.

## Methods and interpretation

**Tools used in the broader research:** AlphaFold Server, AutoDock Vina, Python, molecular visualization, pocket-analysis workflows and OpenMM. These methods were applied at different stages; only the synthetic Python demonstration is independently runnable from the files in this portfolio.

**Scientific interpretation:** The analyzed structures are computational predictions. Candidate interfaces and pockets require independent confirmation; docking scores cannot establish experimental binding, and the archived short MD work cannot demonstrate long-term stabilization. These boundaries are documented concisely in [Methods and evidence](docs/methods_and_evidence.md).

## Repository contents

- `portfolio/`: research case studies in accessible scientific language.
- `qa_auditor/`: runnable Python demonstration and synthetic test suites.
- `docs/`: methods, provenance boundaries and scientific interpretation.

This is a **curated portfolio** separate from the private original research archive. It intentionally excludes source predictions, receptor derivatives, historical docking poses/logs and molecular dynamics trajectories. It is not a complete rerun of the historical research.

## Attribution and reuse

Research direction and scientific evaluation were researcher-led; AI assistance was used for some coding, debugging and documentation. The included software has **no open-source license yet**; code ownership and attribution must be confirmed before a public release. Third-party model outputs and derivatives are not included.
