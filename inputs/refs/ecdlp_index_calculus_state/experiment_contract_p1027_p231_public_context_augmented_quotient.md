# Experiment Contract: P1027 p231 public-context augmented quotient audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1026 RHS obstruction can be isolated by adding explicit public-context basis variables to the quotient matrix, while preserving a nonzero factor-rank component. A viable representation should make seed-plus-fresh quotient rows consistent without reducing the signal to public-context bookkeeping, and should pass held-out public rowspace checks when the held-out equations are testable.

## Null hypothesis
Public-context augmentation only hides the inconsistency in context variables, or remains inconsistent, or provides no held-out public prediction. In that case, the current leaf-19 quotient family is still context-local and not yet a reusable factor-base namespace.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- source selector: P1022 frozen rule `topk4_anchor_leaf19_hybrid_saltgap_ge3_ops_ge_0p7_rank_ge2`
- quotient source: P1026 scope, using seed public `[9131,7063]` plus fresh publics `[8914,3039]` and `[9299,3922]`
- training windows: P1022 positive calibration plus P1022 validation through `12432_12439`
- fresh windows: `12440_12447` through `12496_12503`
- quotient method: same-public form pairs eliminate the first coefficient as `q_right * left - q_left * right`
- modulus/order: `11779`
- context models:
  - `factor_only`
  - `public_onehot_context`
  - `public_xy_context`
  - `public_sumdiff_context`
  - `salt_minmax_context`

## Metrics
- matrix consistency: coefficient rank versus augmented rank
- factor component: full coefficient rank minus context-only rank
- held-out public checks: rowspace implication for held-out public rows where coefficient rows are already in the training rowspace
- context-only risk: whether consistency comes only from nonpredictive public one-hot variables
- promotion: consistent model with nonzero factor component and held-out prediction success

## Positive control
The seed public `[9131,7063]` quotient bank must reproduce rank `2` and matrix consistency.

## Negative control
The `factor_only` model should reproduce the P1026/P1025 global inconsistency rather than silently pass.

## Success criterion
Primary success requires a context model that:

- is matrix-consistent over seed-plus-fresh quotient rows;
- has positive factor component rank;
- has at least one testable held-out public row; and
- passes every testable held-out public rowspace prediction.

Secondary diagnostic success allows a consistent nonpredictive model, but it must be labeled as context bookkeeping rather than factor-base progress.

## Falsification criterion
The representation-change hypothesis is narrowed if no predictive context model satisfies the success criterion. A public one-hot model that merely makes rows consistent without held-out prediction is diagnostic, not a breakthrough.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1027_p231_public_context_augmented_quotient.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1027_p231_public_context_augmented_quotient.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1027_p231_public_context_augmented_quotient_probe.json
```

## Interpretation boundary
This is an index-calculus precursor. A positive result would be a toy representation signal, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-29 18:59:13 PDT
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1027_p231_public_context_augmented_quotient.py --contract ecdlp_index_calculus_state/experiment_contract_p1027_p231_public_context_augmented_quotient.md --out ecdlp_index_calculus_state/low_term_total2_p1027_p231_public_context_augmented_quotient_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1027_p231_public_context_augmented_quotient_probe.json`
- claim: `NEGATIVE_RESULT_P1027_PUBLIC_CONTEXT_AUGMENTATION_NO_PROMOTION`
- controls: training selected `14`, fresh selected `3`, negative controls selected `0`, reconstruction errors `0`, seed quotient rank `2`.
- quotient rows: `10` target-eliminated factor relations across `3` publics and `16` factor columns.
- factor-only baseline: coefficient rank `2`, augmented rank `3`, inconsistent, reproducing the P1026 obstruction.
- public one-hot context: coefficient rank `5`, augmented rank `6`, inconsistent; no held-out rows testable.
- public XY context: coefficient rank `5`, augmented rank `6`, inconsistent; no held-out rows testable.
- public sum/diff context: coefficient rank `5`, augmented rank `6`, inconsistent; no held-out rows testable.
- salt min/max context: coefficient rank `5`, augmented rank `6`, inconsistent; `0/3` held-out tests pass.

## Interpretation
NEGATIVE RESULT under the P1027 representation-change model: explicit public-context or salt-context basis variables do not isolate the RHS shift while preserving a promotable quotient matrix. Even public one-hot bookkeeping fails to make the full seed-plus-fresh quotient system consistent, so the obstruction is not just a missing per-public offset.

The useful narrowing is that inconsistency also lives within richer relation families for public `[9299,3922]`, not only between seed public `[9131,7063]` and fresh publics. The factor component remains rank `2`, but every tested context model has augmented rank one greater than coefficient rank.

## Next concrete action
Create P1028 as a relation-class split audit: separate quotient rows by canonical coefficient family, support size, and q-coefficient pattern before matrix pooling. Test whether any class has consistent factor-rank growth and held-out public prediction. If all useful classes are singleton or inconsistent, record a scoped negative for this leaf-19 quotient family and move to a neighboring motif/representation rather than adding more bookkeeping columns.
