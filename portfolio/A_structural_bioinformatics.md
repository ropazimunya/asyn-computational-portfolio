# A | Structural bioinformatics and analytical judgment

**Target capability:** Computational research scientist, structural bioinformatics.

## Question and work performed

How sensitive are predicted WT and A53T α-synuclein interchain interfaces to model selection? The historical research examined two AlphaFold Server jobs with five predicted models each, interchain confidence, central-residue contact maps and sensitivity to excluding an outlying WT model. Analysis was descriptive, not a statistical comparison of biological replicates.

## Reported historical observations

| Historical metric | WT | A53T |
| --- | ---: | ---: |
| Five-model mean ipTM | 0.208 | 0.266 |
| Central interchain PAE (Å) | 17.541 | 13.881 |
| Mean within-job central contact Jaccard | 0.2963 | 0.4563 |
| Central interchain residue pairs common to all five | 13 | 53 |

Excluding WT model 4 was reported to change WT mean contact Jaccard to **0.4129**. These figures are carried from the historical analysis; the underlying model outputs are retained privately and cannot be independently recomputed from this portfolio. They describe **predictions**, not a verified difference in dimer stability.

## Work demonstrated

Coordinate/confidence interpretation; explicit contact criteria; ensemble comparison; sensitivity analysis; conservative reporting of uncertain structural inferences.

## Scientific decision

The model evidence motivates additional validation, **not** a claim of mutation-driven conformational stabilization or experimentally established cryptic-pocket formation. See [methods and evidence](../docs/methods_and_evidence.md).
