# Input Specification and Disposition Policy

## Archive layout

The synthetic convention requires the ZIP root `asyn-cryptic-pocket-screening-main/`. This name is a fixture convention, not a request to redistribute the private research repository. Under that root the auditor expects:

- `docking/vina_config.txt`
- `run_docking.sh`
- `docking_results_summary.csv`
- `docking/ligands_pdbqt/{ligand}.pdbqt` directly in that directory
- `docking/results_wt/{ligand}.log` and `{ligand}_out.pdbqt`
- equivalent records under `docking/results_a53t/`

## Selected fields

The config requires finite center_x/y/z, positive size_x/y/z and positive integer exhaustiveness. Optional num_modes must be a positive integer; it is not cross-checked against the number of pose models. Other numeric options may be retained without semantic validation. Nonnumeric assignments are outside this synthetic schema.

The summary requires unique headers including Compound, WT_Affinity_kcal_mol and A53T_Affinity_kcal_mol. Nonblank rows must match header width; compound names must be unique. Score fields must be finite. Extra named columns are allowed and are not interpreted.

Logs use the exact labels demonstrated by the fixtures: AutoDock Vina, Grid center, Grid size, Exhaustiveness and random seed. Recognized duplicates or malformed occurrences are errors. The top-score row starts with mode 1 and has zero RMSD fields. Unsupported real log formats can be rejected; real Vina compatibility is not established.

Pose REMARK VINA RESULT lines require three finite numbers. Multiple valid lines represent multiple poses; the first is compared. Malformed recognized lines are errors even if the first score agrees.

## Numerical and review policies

Expected version defaults to 1.2.7 and can be supplied by CLI option. Score differences up to 0.00100001 are accepted. Coordinate agreement uses relative tolerance 1e-8 and absolute tolerance 1e-6. These policies are synthetic test conventions, not empirically validated real-log rounding rules.

Seeds are required and parsed as signed integers. Reuse across runs generates DUPLICATE_SEED_REVIEW and a nonzero overall exit even when intentionally paired; this requests assessment and does not prove a scientific defect. Observed seeds are not compared with a trusted external execution manifest.

## Reports

The CLI writes run_audit.csv, exceptions.csv, source_manifest.csv and audit_summary.json. Exit 0 means no recorded issues; exit 1 means at least one issue, including a review flag. Argparse usage errors use its own nonzero status. Known terminal archive errors generate four terminal reports when the destination is writable. Direct Python main callers must handle terminal exceptions themselves.

A run disposition fails if a selected comparison fails or a linked run/ligand exception exists. Verified-primary-run count includes only passing run dispositions. Global archive errors may still make the entire audit fail even if some runs pass. This count does not certify molecular validity. Script text indicators mean literal occurrence, including comments, not executable behavior or proof of execution.

## Resource and integrity limits

Declared uncompressed members are limited to 32 MiB each and 256 MiB overall. Reads are not a comprehensive hostile-archive defense. No files are extracted. Member and archive hashes identify observed bytes; there is no trusted-reference hash verification. Coordinated cross-file changes can evade consistency checks. Output writes are not a transactional storage system. Use a fresh output directory and inspect process status as well as reports.
