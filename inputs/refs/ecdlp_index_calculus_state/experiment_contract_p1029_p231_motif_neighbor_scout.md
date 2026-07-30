# Experiment Contract: P1029 p231 motif-neighbor scout

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: a neighboring total-2 leaf motif may preserve the P1022 clean scalar signal while changing the raw form or quotient relation structure that made the leaf-19 quotient pool inconsistent.

## Null hypothesis
Neighboring motifs either do not appear under the public core guard, are noisier than leaf-19, collapse to duplicate row-key variants, or reproduce inconsistent/dependent relation banks. Then the next positive search should move from neighboring leaf tuples to a representation change, not more leaf-19 quotient bookkeeping.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- reference selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- scout selector: `mode_cost_hybrid_support_monic_b_total2`, `salt_gap >= 3`, `source_ops_over_rho >= 0.7`, `source_rank >= 2`, grouped by `unique_leaf_indices`; top-k and exact anchor row-key are relaxed
- training windows: P1022 positive calibration plus P1022 validation through `12432_12439`
- negative controls: `12224_12231`, `12264_12271`, `12320_12327`
- fresh windows: `12440_12447` through `12496_12503`
- quotient method: same-public form pairs eliminate the first coefficient as `q_right * left - q_left * right`
- modulus/order: `11779`
- baseline: Pollard rho remains the one-target scalar baseline; this audit measures relation precursor structure

## Metrics
- selected row count, positive count, false count, precision
- fresh positive and fresh false counts
- unique row-key signature count
- top-k distribution
- raw form coefficient rank and augmented rank
- target-eliminated quotient relation count, coefficient rank, augmented rank, and consistency
- duplicate-compressed row-key audit for relation-bank stability

## Positive control
The reference leaf-19 selector must reproduce the P1025 shape over training plus fresh windows: training selected `14`, fresh selected `3`, negative controls selected `0`, and zero selected false positives.

## Negative control
A neighbor motif is not promotable if it selects any negative-control row, any fresh false row, or only duplicate row-key variants without relation-bank improvement.

## Success criterion
Primary success requires a non-leaf-19 motif with:

- at least one fresh positive row;
- zero selected false rows in negative controls and fresh validation;
- at least two unique row-key signatures after duplicate compression; and
- either a consistent raw form matrix with positive rank or a consistent target-eliminated quotient matrix with positive factor rank that is not merely the leaf-19 reference rank.

## Falsification criterion
If every non-leaf-19 motif is absent, noisy, duplicate-only, or relation-bank inconsistent/dependent, this is a scoped negative for neighboring leaf tuples under the current total-2 selector. It does not rule out index calculus; it redirects the next positive search to representation changes.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1029_p231_motif_neighbor_scout.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1029_p231_motif_neighbor_scout.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1029_p231_motif_neighbor_scout_probe.json
```

## Interpretation boundary
This is an index-calculus precursor experiment. A positive result would be a toy relation-motif signal, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-30T02:18:37Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1029_p231_motif_neighbor_scout.py --contract ecdlp_index_calculus_state/experiment_contract_p1029_p231_motif_neighbor_scout.md --out ecdlp_index_calculus_state/low_term_total2_p1029_p231_motif_neighbor_scout_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1029_p231_motif_neighbor_scout_probe.json`
- claim: `P1029_NEIGHBOR_MOTIF_SCALAR_SIGNAL_NOISY_NOT_PROMOTABLE`
- positive control: reference leaf `[19]` reproduced `17` selected rows, `17` positives, zero false selections, `3` fresh positives, and zero negative-control selections.
- scout motifs: `2` motifs observed under the relaxed selector: `[19]` and neighbor `[8]`.
- neighbor `[8]` scalar signal: `12` selected rows, `10` positives, `2` false rows, precision `0.83333333`, `4` fresh rows, `3` fresh positives, `1` fresh false, and zero negative-control selections.
- duplicate boundary: leaf `[8]` has `12` case-level rows but only `8` unique row-key signatures; top-k variants are a real duplication risk.
- leaf `[8]` case-level relation audit: raw form rank/augmented `3/4`, inconsistent; target-eliminated quotient relation count `30`, quotient rank/augmented `2/3`, inconsistent.
- leaf `[8]` row-signature-compressed audit: raw form rank/augmented `3/4`, inconsistent; target-eliminated quotient relation count `26`, quotient rank/augmented `2/3`, inconsistent.
- reference leaf `[19]` row-signature-compressed audit remains the known P1028 boundary: raw form rank/augmented `3/4`, quotient rank/augmented `2/3`, inconsistent.

## Interpretation
OBSERVATION / NOT PROMOTABLE: relaxing top-k and exact anchor row-key exposes a neighboring leaf `[8]` scalar signal with fresh positives, but it fails the clean-scheduler gate because it selects a fresh false row. The relation-bank audit does not rescue it: after duplicate row-key compression, both raw forms and target-eliminated quotient rows remain augmented-inconsistent.

This is a scoped negative for nearby total-2 leaf-tuple motifs under the current selector. It does not argue against index calculus. It narrows the obstruction: the issue is not only leaf `[19]`; at least one adjacent total-2 representation also falls into the same low-rank/inconsistent augmented-matrix pattern.

## Next concrete action
Move from neighboring leaf tuples to a representation-change audit. P1030 should test a quotient-normalized or coordinate-changed representation that changes the RHS model before relation pooling, rather than only changing selected leaf indices.
