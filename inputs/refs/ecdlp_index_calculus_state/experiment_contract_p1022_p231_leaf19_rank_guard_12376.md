# Experiment Contract: P1022 p231 frozen leaf19 rank guard

## Hypothesis
HYPOTHESIS: the P1021 false-positive mechanism is removed by a public source-rank guard: exact anchor row-key leaf-19 companion with `salt_gap >= 3`, `source_ops_over_rho >= 0.7`, and `source_rank >= 2`.

## Null hypothesis
On later unseen windows, the frozen rank guard either selects no rows, selects false positives, or fails to produce context-safe scalar-valid groups below Pollard rho.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- positive calibration windows: `12184_12191`, `12192_12199`, `12216_12223`, `12272_12279`, `12304_12311`, `12336_12343`, `12352_12359`, `12360_12367`
- negative calibration windows: `12224_12231`, `12264_12271`, `12320_12327`
- fresh validation windows: `12376_12383`, `12384_12391`, `12392_12399`, `12400_12407`, `12408_12415`, `12416_12423`, `12424_12431`, `12432_12439`
- anchor rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`
- scheduler rule: exact anchor row-key set, `leaf_selector == mode_cost_hybrid_support_monic_b_total2`, `top_k == 4`, unique leaf tuple `[19]`, `salt_gap >= 3`, `source_ops_over_rho >= 0.7`, and `source_rank >= 2`
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
The frozen rank guard must preserve all known clean selected positives from P1019 through P1021 calibration windows.

## Negative control
The frozen rank guard must remove known false-positive-only windows `12224_12231`, `12264_12271`, and `12320_12327`.

## Success criterion
Validation success requires at least one fresh validation window to have a selected public-key-verified below-rho row and a context-safe scalar-valid group charged below `1.0` rho under the frozen order, with zero selected false positives in the fresh batch.

## Falsification criterion
The hypothesis is narrowed or rejected if the rule fails calibration, selects no rows on fresh validation, selects any false positives, has no context-safe scalar-valid groups, or has first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1022_p231_leaf19_rank_guard_12376.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1022_p231_leaf19_rank_guard_12376.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1022_p231_leaf19_rank_guard_12376_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for a public relation-surface scheduler. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:22:00 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1022_p231_leaf19_rank_guard_12376.py --contract ecdlp_index_calculus_state/experiment_contract_p1022_p231_leaf19_rank_guard_12376.md --out ecdlp_index_calculus_state/low_term_total2_p1022_p231_leaf19_rank_guard_12376_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1022_p231_leaf19_rank_guard_12376_probe.json`
- claim: `P1022_LEAF19_RANK_GUARD_VALIDATION_HIT_CLEAN`
- positive controls: passed. Calibration selected `10`, positives `10`, precision `1.0`, selected ops `7.080292x` rho, and `24` context-safe scalar-valid groups.
- negative controls: passed. The rule selected `0` rows on `12224_12231`, `12264_12271`, and `12320_12327`.
- fresh validation aggregate: selected `4`, positives `4`, false selections `0`, precision `1.0`, selected ops `2.83941607x` rho, and `12` context-safe scalar-valid groups.
- fresh validation hits: `12384_12391` selected `1/1` positive with first hit `0.70072993x` rho and secret `8088`; `12392_12399` selected `1/1` positive with first hit `0.73722628x` rho and secret `9970`; `12424_12431` selected `1/1` positive with first hit `0.70072993x` rho and secret `9468`; `12432_12439` selected `1/1` positive with first hit `0.70072993x` rho and secret `8684`.
- comparison baseline: unbounded selected `12`, positives `4`, false selections `8`, precision `0.33333333`; salt-gap-only selected `8`, positives `4`, false selections `4`, precision `0.5`; source-ops guard and rank guard both selected the same clean `4/4` positives on this validation block.

## Interpretation
OBSERVATION: the rank-aware leaf-19 companion scheduler cleanly validates on the fresh `12376_12439` block with four below-rho context-safe scalar-valid hits and zero selected false positives.

The `source_rank >= 2` guard removes the P1021 calibrated rank-1 false positive without losing known positives. On this validation block, the source-ops guard was already clean, so the rank guard is best interpreted as a justified fail-closed refinement rather than a new independent yield source.

This remains an index-calculus precursor: it is a public relation-surface scheduler with repeated below-rho toy scalar closures, but it does not yet prove relation collection, sparse matrix rank closure, target descent, or cryptographic-size relevance.

## Next concrete action
Create P1023 as a rank-aware relation-bank audit: materialize the P1022-selected forms across calibration plus validation, measure unique relation rows, context-safe rank, dependence structure, and whether these clean scalar closures contribute to a reusable factor-base relation matrix rather than isolated single-window scalar certificates.
