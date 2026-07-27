# Experiment Contract: P1021 p231 frozen leaf19 source-ops guard

## Hypothesis
HYPOTHESIS: the clean P1020 diagnostic rule, exact anchor row-key leaf-19 companion with `salt_gap >= 3` and `source_ops_over_rho >= 0.7`, remains a clean public relation-surface scheduler on later unseen windows.

## Null hypothesis
On later unseen windows, the frozen source-ops guard either selects no rows, selects false positives, or fails to produce context-safe scalar-valid groups below Pollard rho.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- positive calibration windows: `12184_12191`, `12192_12199`, `12216_12223`, `12272_12279`, `12304_12311`
- negative calibration windows: `12224_12231`, `12264_12271`
- fresh validation windows: `12312_12319`, `12320_12327`, `12328_12335`, `12336_12343`, `12344_12351`, `12352_12359`, `12360_12367`, `12368_12375`
- anchor rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`
- scheduler rule: exact anchor row-key set, `leaf_selector == mode_cost_hybrid_support_monic_b_total2`, `top_k == 4`, unique leaf tuple `[19]`, `salt_gap >= 3`, and `source_ops_over_rho >= 0.7`
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
The frozen source-ops guard must preserve the known clean selected positives from P1019/P1020 calibration windows.

## Negative control
The frozen source-ops guard must remove the known false-positive-only windows `12224_12231` and `12264_12271`.

## Success criterion
Validation success requires at least one fresh validation window to have a selected public-key-verified below-rho row and a context-safe scalar-valid group charged below `1.0` rho under the frozen order, with zero selected false positives in the fresh batch.

## Falsification criterion
The hypothesis is narrowed or rejected if the rule fails calibration, selects no rows on fresh validation, selects any false positives, has no context-safe scalar-valid groups, or has first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1021_p231_leaf19_ops_guard_12312.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1021_p231_leaf19_ops_guard_12312.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1021_p231_leaf19_ops_guard_12312_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for a public relation-surface scheduler. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:17:01 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1021_p231_leaf19_ops_guard_12312.py --contract ecdlp_index_calculus_state/experiment_contract_p1021_p231_leaf19_ops_guard_12312.md --out ecdlp_index_calculus_state/low_term_total2_p1021_p231_leaf19_ops_guard_12312_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1021_p231_leaf19_ops_guard_12312_probe.json`
- claim: `P1021_LEAF19_OPS_GUARD_VALIDATION_HIT_WITH_NOISE`
- positive controls: passed. Calibration selected `6`, positives `6`, precision `1.0`, selected ops `4.24087593x` rho, and `15` context-safe scalar-valid groups.
- negative controls: passed. The rule selected `0` rows on `12224_12231` and `12264_12271`.
- fresh validation aggregate: selected `5`, positives `4`, false selections `1`, precision `0.8`, selected ops `3.540146x` rho, and `9` context-safe scalar-valid groups.
- fresh validation hits: `12336_12343` selected `1/1` positive with first hit `0.70072993x` rho and secret `8246`; `12352_12359` selected `2/2` positives with first hit `0.70072993x` rho and secret `5618`; `12360_12367` selected `1/1` positive with first hit `0.73722628x` rho and secret `7885`.
- fresh validation noise: `12320_12327` selected one false row, row keys `salt164+salt167`, salt gap `3`, transfer offset `0`, source ops `0.70072993x` rho, source rank `1`.
- comparison baseline: unbounded and salt-gap-only both selected `11`, positives `4`, false selections `7`, precision `0.36363636`; the source-ops guard improved precision to `0.8` while preserving the same three scalar-success windows.

## Interpretation
OBSERVATION: the frozen source-ops guard generalizes to a later disjoint block with three below-rho scalar-valid success windows and substantially better precision than the unbounded or salt-gap-only rules. It is not clean because `12320_12327` produced one false selected row.

The false-positive mechanism is now narrow: the remaining false row has source rank `1`, while the fresh positives in this batch have source rank `2` or `3`. This suggests a public rank-aware guard as the next falsifiable refinement.

This remains an index-calculus precursor: the branch improves relation-surface scheduling and below-rho toy scalar closure, but does not yet establish relation collection, sparse matrix rank closure, target descent, or cryptographic-size relevance.

## Next concrete action
Create P1022 by freezing `salt_gap >= 3 AND source_ops_over_rho >= 0.7 AND source_rank >= 2`, then validate unchanged on later disjoint windows after `12375`. The success criterion should require at least one below-rho context-safe scalar-valid hit with zero selected false positives.
