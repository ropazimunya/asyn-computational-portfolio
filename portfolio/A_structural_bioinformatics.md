# A Structural Bioinformatics and Analytical Judgment

## Research question

How sensitive are apparent WT and A53T α-synuclein interfaces to the choice of predicted model? The private scientific archive contains descriptive measurements for five predictions per target. Outputs from one modeling job are correlated samples, not independent biological replicates.

## Analysis and evidence

The archived table permits arithmetic checks of per-model confidence and NAC geometry summaries. A low-confidence WT model strongly influences a reported centroid-distance mean; the WT model-selection sensitivity is therefore central to interpretation. The source inspection is recorded in the [source register](../evidence/SOURCE_REGISTER.md).

This portfolio does not distribute AlphaFold structures, their numerical structural tables or derived figures. The complete ensemble coordinates, confidence JSONs and original metric-generation scripts were not supplied in the inspected scientific ZIP; only model-0 coordinates were present. Arithmetic agreement in a derived table does not independently validate the coordinate calculations behind it.

## Analytical decision

Model exclusion is a sensitivity analysis that must be justified and reported, not a way to improve an apparent result. Model-selection dependence prevents a confident mutation-associated packing conclusion. Confidence scores are not stability, affinity or experimental evidence. A predicted interface or geometric cavity alone does not establish a physiological dimer or a cryptic pocket.

## Methods needed for full reproduction

A coordinate-based reproduction would need explicit residue selections, chain mapping, atom selection, distance thresholds, periodic/alignment conventions, contact-set definitions, model-wise inputs and aggregation rules. Several of those definitions remain incomplete in the available historical record. I do not invent them to fill the gap.

## Skills represented

Confidence interpretation, ensemble inspection, sensitivity assessment and conservative scientific reporting. These are documented historical activities; the independently runnable public demonstration is [Case B](B_quality_assurance_control.md).
