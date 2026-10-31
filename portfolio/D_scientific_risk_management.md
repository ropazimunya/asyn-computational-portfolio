# D | Scientific Risk Assessment & Risk Management

**Target capability:** Quality Risk Management, Quality Systems, scientific evidence governance.

## Decision context

**Context of use:** Decide whether computational outputs are appropriate to communicate as exploratory research and whether each proposed statement is proportionate to supporting evidence. This is **not** an assessment of patient safety or a regulated product hazard analysis.

## Public-facing risk-control examples

The table demonstrates risk-based analysis without reproducing the private project risk register. **Qualitative priorities are illustrative screening judgments**, not validated probabilities.

| Risk scenario | Potential consequence | Mitigation / control | Evidence needed before stronger claims |
| --- | --- | --- | --- |
| Low-confidence predicted dimer interface | Treating one predicted configuration as physiological | Compare model ensemble; explicitly report confidence and variability | Orthogonal structural or biochemical evidence |
| Model-selection dependence | Apparent differences driven by selected predicted model | Model-wise contact assessment and sensitivity analyses | Independent conformations and robust sensitivity checks |
| Inconsistent computational execution records | Unsupported methods narrative or untraceable scores | Automated checks of settings, inputs, logs, poses and summaries | Reproducible source records and independent rerun |
| Short, limited MD sampling | Overinterpreting transient contacts as stabilization | Report sampled timescale, controls, replicates and uncertainty | Appropriate extended sampling, replicates and experimental evidence |
| Unsupported regulatory or therapeutic language | Misleading readers about the study's intended use | Claim-to-evidence review and nonclinical scope statement | Suitable analytical, preclinical and regulatory evidence for the claimed use |

## Risk-management workflow demonstrated

**Define context → identify failure modes → evaluate consequences and uncertainty → select controls → verify control performance → communicate remaining limitations.**

The concrete verification example is [Chunk B](B_quality_assurance_control.md): testing designed faults before and after a software control improvement. This supports detection within the synthetic scenario; it does not erase all downstream scientific uncertainty. Risk disposition remains a **context-specific professional judgment** rather than a universal PASS/FAIL rating.

## Limitations

This is a portfolio reconstruction of risk-based reasoning from the historical project, not the entire 13-item private register. There are no calibrated likelihoods, prospective risk thresholds, formal ISO 14971 implementation, GxP sign-off or regulatory acceptance claims.
