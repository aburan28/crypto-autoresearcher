# Experiment Contract: P1026 p231 affine-RHS obstruction audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1025 seed-plus-fresh quotient inconsistency may be caused by a public-computable affine RHS offset. If repeated target-eliminated coefficient vectors differ only by a predictable public, row-key, or salt-pair offset, then normalizing RHS values could turn local quotient rows into a reusable factor-bank namespace.

## Null hypothesis
Repeated quotient coefficient vectors have RHS differences that are not explained by low-parameter public-coordinate, row-key, or salt-pair affine models with held-out prediction. In that case, the current raw leaf-19 quotient representation remains context-local.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- seed public: `[9131,7063]`
- fresh publics from P1025: `[8914,3039]` and `[9299,3922]`
- training windows: P1022 positive calibration plus P1022 validation through `12432_12439`
- fresh windows: `12440_12447` through `12496_12503`
- quotient method: same-public form pairs eliminate the first coefficient as `q_right * left - q_left * right`, then canonicalize factor coefficients modulo order `11779`
- models tested: constant RHS, one-variable public affine models, two-variable public affine interpolation, one-variable salt affine models, and two-variable salt affine interpolation
- promotion rule: an affine normalization is viable only if it is exact on the cluster and passes leave-one-public-out prediction whenever the model has enough rank for a unique held-out prediction

## Metrics
- quotient rows: total target-eliminated rows and repeated-coefficient clusters
- RHS collisions: distinct RHS count per canonical coefficient vector
- public coverage: distinct public fingerprints per cluster
- model fit: exact fit, feature rank, leave-one-out tested count, leave-one-out pass count
- promotion: low-parameter held-out-predictive normalization candidates

## Positive control
The audit must reproduce the P1025 selected shape, seed quotient rank `2/16`, and the repeated coefficient vector `[0,1,1,0,...]` across seed/fresh publics.

## Negative control
The known P1022 false-positive control windows must still select `0` rows.

## Success criterion
Primary success requires at least one repeated-coefficient RHS-collision cluster to have a public-computable or salt-computable affine model that:

- fits all observed RHS values exactly modulo `11779`;
- is not merely an underdetermined interpolation; and
- passes all testable leave-one-public-out predictions.

## Falsification criterion
The affine-RHS normalization hypothesis is narrowed if repeated coefficient vectors remain inconsistent under all low-parameter held-out-predictive affine models. Exact full-rank interpolation without held-out predictability is not sufficient.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1026_p231_affine_rhs_obstruction_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1026_p231_affine_rhs_obstruction_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1026_p231_affine_rhs_obstruction_audit_probe.json
```

## Interpretation boundary
This is an index-calculus precursor. A positive result would be a candidate normalization for toy quotient rows, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:54:07 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1026_p231_affine_rhs_obstruction_audit.py --contract ecdlp_index_calculus_state/experiment_contract_p1026_p231_affine_rhs_obstruction_audit.md --out ecdlp_index_calculus_state/low_term_total2_p1026_p231_affine_rhs_obstruction_audit_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1026_p231_affine_rhs_obstruction_audit_probe.json`
- claim: `NEGATIVE_RESULT_P1026_AFFINE_RHS_OBSTRUCTION_STANDS`
- controls: training selected `14`, fresh selected `3`, negative controls selected `0`, reconstruction errors `0`, seed quotient rank `2`.
- quotient rows: `10` target-eliminated factor relations in scope, with `1` repeated-coefficient cluster and `1` RHS-collision cluster.
- obstruction cluster: coefficient vector `[0,1,1,0,...]` occurs across publics `[8914,3039]`, `[9131,7063]`, and `[9299,3922]` with RHS values `11023`, `1025`, and `11023`.
- low-parameter models: constant, `public_x`, `public_y`, `public_sum`, `public_diff`, `public_product`, `salt_sum`, `salt_gap`, `salt_min`, and `salt_max` affine models all fail exact fit or held-out prediction.
- interpolation boundary: `public_xy_interpolation` fits the three samples exactly, but has `0` leave-one-out tested predictions and is non-promotable under the preregistered rule.

## Interpretation
NEGATIVE RESULT under the P1026 low-parameter normalization model: the observed RHS mismatch for repeated quotient vector `[0,1,1,0,...]` is not explained by the tested public-coordinate or salt-pair affine normalizers.

This narrows P1025's obstruction. The issue is not merely that we forgot a simple public or salt affine offset. The current raw leaf-19 quotient representation remains context-local unless a richer representation explains the RHS shift with held-out prediction.

The exact three-parameter public interpolation is not promoted because it has no predictive degree of freedom on three samples. It is a diagnostic pointer, not a usable normalization.

## Next concrete action
Create P1027 as a representation-change test rather than another scalar scheduler: lift quotient rows into an augmented namespace with explicit public-context basis variables, then test whether context variables isolate the RHS shift while preserving factor-rank growth. Success requires a consistent augmented matrix with a nonzero factor-rank component and held-out public prediction; failure becomes a scoped negative for public-context augmentation of this leaf-19 quotient family.
