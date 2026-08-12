# Experiment Contract: P1019 p231 unbounded leaf19 companion scheduler

## Hypothesis
HYPOTHESIS: the public unbounded leaf-19 companion rule, exact anchor row-key set plus `mode_cost_hybrid_support_monic_b_total2` top-k4 leaf tuple `[19]`, remains a useful sparse relation-surface scheduler on later unseen windows.

## Null hypothesis
On later unseen windows, the unbounded leaf-19 companion rule either selects no rows, selects only false positives, or fails to produce context-safe scalar-valid groups below Pollard rho.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- controls: `12184_12191`, `12192_12199`
- validation windows: `12216_12223`, `12224_12231`, `12232_12239`, `12240_12247`, `12248_12255`
- anchor rule: `top_k == 4 AND leaf_selector == mode_cost_low_term_support_total2`
- scheduler rule: exact anchor row-key set, `leaf_selector == mode_cost_hybrid_support_monic_b_total2`, `top_k == 4`, unique leaf tuple `[19]`
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
The rule must reproduce below-rho context-safe scalar hits on `12184_12191` and `12192_12199`.

## Negative control
False-positive selected windows are reported as part of batch precision and cannot be dropped post-hoc.

## Success criterion
Validation success requires at least one later unseen window to have a selected public-key-verified below-rho row and a context-safe scalar-valid group charged below `1.0` rho under the frozen order.

## Falsification criterion
The hypothesis is narrowed or rejected if validation windows select no rows, no public-key-verified below-rho rows, no context-safe scalar-valid groups, or first scalar-valid hits charged at or above `1.0` rho.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1019_p231_leaf19_companion_unbounded_12216.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1019_p231_leaf19_companion_unbounded_12216.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1019_p231_leaf19_companion_unbounded_12216_probe.json
```

## Interpretation boundary
This is `TOY-EVIDENCE` for sparse relation-surface scheduling. A hit is an index-calculus precursor only; it is not relation collection, sparse linear algebra, target descent, cryptographic-size evidence, or a deployable faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:03:39 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1019_p231_leaf19_companion_unbounded_12216.py --contract ecdlp_index_calculus_state/experiment_contract_p1019_p231_leaf19_companion_unbounded_12216.md --out ecdlp_index_calculus_state/low_term_total2_p1019_p231_leaf19_companion_unbounded_12216_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1019_p231_leaf19_companion_unbounded_12216_probe.json`
- claim: `P1019_LEAF19_COMPANION_VALIDATION_HIT_WITH_NOISE`
- controls: both positive controls passed. `12184_12191` selected `1/1` positive with first scalar-valid hit `0.70072993x` rho and secret `1618`; `12192_12199` selected `1/1` positive with first scalar-valid hit `0.70072993x` rho and secret `3353`.
- validation aggregate: selected `3`, positives `2`, precision `0.66666667`, selected ops `2.06569344x` rho, context-safe scalar-valid groups `3`.
- validation hit: `12216_12223` selected `2/2` positives, first fixed-order scalar-valid hit `0.70072993x` rho, derived secret `7955`, row keys `salt165+salt168`.
- validation noise: `12224_12231` selected `1` false-positive row at `0.66423358x` rho with row keys `salt173+salt174`.
- quiet validation windows: `12232_12239`, `12240_12247`, and `12248_12255` selected no rows.

## Interpretation
OBSERVATION: the frozen unbounded leaf-19 companion scheduler transfers to later unseen windows and produces a below-rho context-safe scalar-valid hit, but it is not clean because one selected validation window is a false positive and three later windows are quiet.

This is an index-calculus precursor signal: it improves the relation-surface scheduler beyond the failed max-salt guard, but it does not yet establish relation collection, rank closure, target descent, or a faster-than-rho ECDLP algorithm.

## Next concrete action
Create a P1020 precision-and-recurrence audit that keeps the unbounded leaf-19 rule but tests public refinements around row-key salt gaps, transfer offsets, and repeated `salt165` anchors. The next success criterion should preserve the `12216_12223` hit while removing the `12224_12231` false positive, then validate on a fresh disjoint block.
