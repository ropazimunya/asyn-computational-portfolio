# C Molecular Modeling and Scientific Interpretation

## Historical workflow

The scientific archive contains receptor and ligand preparation files, docking logs, pose files, summary tables and pocket-analysis records. It documents historical AutoDock Vina work and an OpenMM preparation investigation. The public portfolio does not execute docking or MD and does not distribute these molecular artifacts.

## What has been checked

A read-only independent parser compared the first-ranked score in each of 24 primary logs with the first pose-score remark and its summary entry. All 24 agreed numerically. This is a check of archived records, not an independent docking rerun or evidence of binding. The extra WT anle138b_out.log is outside the 24 primary records and remains separately classified.

## Ligand-preparation investigation

A historical reconstruction report identifies an atom-order/coordinate-mapping error in the original MD preparation. It reports correction through molecular-graph correspondence and checks of bond geometry and contacts. The supplied corrected ligand's checksum matches the report. That checksum establishes file identity, not chemical correctness or successful repair of a simulation.

The faulty input, trajectories and complete reconstruction scripts were not supplied. I therefore treat the geometry-error diagnosis and corrected-geometry measurements as historical findings, not independently reproduced findings. The same report states that the reconstructed pose did not overlap an fpocket cavity under its tested criterion; that conclusion also remains dependent on unavailable underlying cavity inputs.

## Scientific disposition

The original MD-derived stability interpretation is withheld. Later comparative trajectories cannot be assumed to repair the earlier preparation issue: each system needs its own input lineage and verification. Short unreplicated trajectories cannot establish causal stabilization, residence time or therapeutic activity even if their preparation is sound.

This case demonstrates workflow exposure, error recognition and impact assessment. [Investigation 001](../quality/INVESTIGATION_001.md) and the [claim matrix](../evidence/CLAIM_EVIDENCE_MATRIX.csv) distinguish independently checked records from historical reports.
