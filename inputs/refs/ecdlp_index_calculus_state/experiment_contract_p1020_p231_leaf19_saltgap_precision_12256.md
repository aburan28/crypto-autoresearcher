# Experiment Contract: P1020 p231 leaf19 salt-gap precision audit

## Hypothesis
HYPOTHESIS: the P1019 unbounded leaf-19 companion scheduler can be made cleaner with a public salt-gap guard: exact anchor row-key set plus `mode_cost_hybrid_support_monic_b_total2`, `top_k == 4`, leaf tuple `[19]`, and row-key salt gap at least `3`.

## Null hypothesis
On fresh later windows, the salt-gap guard either selects no rows, selects false positives, or fails to produce context-safe scalar-valid groups below Pollard rho.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- positive calibration windows: `12184_12191`, `12192_12199`, `12216_12223`
- negative calibration window: `12224_12231`
- fresh validation windows: `12256_12263`, `12264_12271`, `12272_12279`, `12280_12287`, `12288_12295`, `12296_12303`, `12304_12311`
- anchor rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`
- base scheduler: exact anchor row-key set, `leaf_selector == mode_cost_hybrid_support_monic_b_total2`, `top_k == 4`, unique leaf tuple `[19]`
- primary precision guard: `salt_gap >= 3`
- baseline: Pollard rho charged as `1.0` ops-over-rho
- frozen order: `salt_gap_asc_ops`

## Metrics
- group operations: charged `source_ops_over_rho`
- field operations: inherited from source artifact ledgers
- memory: selected row count and reconstructed form count only
- relation probability: selected public-key-verified below-rho count over selected count
- rank: source rank and context-safe scalar-valid group count
- solver degree: not applicable to this component audit
- wall-clock: script runtime

## Positive control
The primary rule must preserve the three known below-rho leaf-19 successes in `12184_12191`, `12192_12199`, and `12216_12223`.

## Negative control
The primary rule must remove the P1019 false-positive row in `12224_12231`.

## Success criterion
Validation success requires at least one fresh validation window to have a selected public-key-verified below-rho row and a context-safe scalar-valid group charged below `1.0` rho under the frozen order. A clean validation additionally requires zero selected false positives in the fresh batch.

## Falsification criterion
The hypothesis is narrowed or rejected if the primary rule fails calibration, selects no rows on fresh validation, selects only false positives, has no context-safe scalar-valid groups, or has first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1020_p231_leaf19_saltgap_precision_12256.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1020_p231_leaf19_saltgap_precision_12256.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1020_p231_leaf19_saltgap_precision_12256_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for a public relation-surface scheduler. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:13:19 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1020_p231_leaf19_saltgap_precision_12256.py --contract ecdlp_index_calculus_state/experiment_contract_p1020_p231_leaf19_saltgap_precision_12256.md --out ecdlp_index_calculus_state/low_term_total2_p1020_p231_leaf19_saltgap_precision_12256_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1020_p231_leaf19_saltgap_precision_12256_probe.json`
- claim: `P1020_LEAF19_SALTGAP_VALIDATION_HIT_WITH_NOISE`
- positive controls: passed. The primary salt-gap rule preserved `12184_12191`, `12192_12199`, and `12216_12223` with calibration precision `1.0`, selected `4`, positives `4`, selected ops `2.80291972x` rho, and `9` context-safe scalar-valid groups.
- negative control: passed. The primary rule selected `0` rows in `12224_12231`, removing the P1019 salt-gap-1 false positive.
- fresh validation aggregate: selected `4`, positives `2`, false selections `2`, precision `0.5`, selected ops `2.69343067x` rho, and `3` context-safe scalar-valid groups.
- fresh validation hit: `12304_12311` selected `1/1` positive with first fixed-order scalar-valid hit `0.73722628x` rho and derived secret `2421`, row keys `salt164+salt167`, salt gap `3`.
- fresh relation-supply positive without scalar closure under the primary rule: `12272_12279` selected one true row `salt165+salt168` and one false row `salt165+salt177`; primary fixed-order scalar closure failed in that mixed window.
- fresh validation noise: false-only `12264_12271` selected `salt164+salt171`; noisy `12272_12279` selected one true and one false row.
- diagnostic comparison: the stricter public rule `salt_gap >= 3 AND source_ops_over_rho >= 0.7` selected `2`, positives `2`, false selections `0`, precision `1.0`, selected ops `1.43795621x` rho, and `6` context-safe scalar-valid groups on `12272_12279` and `12304_12311`.

## Interpretation
OBSERVATION: the salt-gap guard is a real precision improvement over P1019's unbounded scheduler and validates a fresh below-rho scalar hit, but it is still noisy as a primary pre-registered rule.

The clean `source_ops_over_rho >= 0.7` diagnostic is promising, but it is not promoted by P1020 because it was a diagnostic variant scored after the primary rule was fixed. It should be frozen in P1021 and validated on later disjoint windows before being treated as a cleaner scheduler.

This remains an index-calculus precursor: the branch has a repeatable public relation-surface selector with below-rho toy scalar closures, but it has not yet shown relation collection, rank closure, target descent, or cryptographic-size relevance.

## Next concrete action
Create P1021 by freezing `exact anchor row-key leaf19 companion AND salt_gap >= 3 AND source_ops_over_rho >= 0.7`, then validate it unchanged on fresh windows after `12311`. The success criterion should require at least one below-rho context-safe scalar-valid fresh hit with zero selected false positives.
