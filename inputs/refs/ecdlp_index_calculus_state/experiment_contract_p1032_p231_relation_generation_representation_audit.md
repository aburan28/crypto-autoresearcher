# Experiment Contract: P1032 p231 relation-generation representation audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1030/P1031 augmented-rank obstruction may be caused by using the wrong relation object before target elimination. A useful index-calculus precursor would be a public or Kummer/slice factor-label rule that merges multiple verifier forms into a consistent pre-elimination linear system while sharing the target variable by public key or x-only Kummer class.

## Null hypothesis
Only per-form factor labels are consistent. Every tested nontrivial merge rule, even with a free per-public target variable, leaves an augmented-rank gap or needs a target variable so local that it cannot support cross-slice factor-base reuse.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scopes:
  - row-signature-compressed P1022 reference leaf `[19]`
  - row-signature-compressed P1029 neighbor leaf `[8]`
- source windows:
  - training: P1022 positive calibration plus validation through `12432_12439`
  - negative controls: `12224_12231`, `12264_12271`, `12320_12327`
  - fresh: `12440_12447` through `12496_12503`
- modulus/order: `11779`
- pre-elimination equation model:
  - each verifier form is treated as `q * target_context + factor_coefficients = rhs mod order`
  - factor labels are assigned by the tested representation rule
  - target labels are assigned by public fingerprint, x-only Kummer coordinate, row key, or form identity depending on the control
- tested representation families:
  - global factor index;
  - public-slice factor index;
  - Kummer x-only factor and target classes;
  - row-key and salt-pair slice factor classes;
  - support-pattern and split-slice factor classes;
  - deterministic random bucket control;
  - per-form positive controls.

## Metrics
- selected row count, fresh positive count, and fresh false count per scope
- unique pre-elimination form count
- factor label count, target label count, and compression ratio versus per-form labels
- coefficient rank and augmented rank
- matrix consistency
- multi-form factor-key count and maximum forms per factor key
- held-out public tested/passed/skipped counts
- primary relation-object merge count
- diagnostic-only local object count

## Positive control
The `control_form_factor_public_target` model must be consistent. It gives every form its own factor labels but still shares the target variable by public fingerprint. This proves the pre-elimination row builder can represent the forms before any merge is attempted.

## Negative control
The `negative_global_factor_public_target` and deterministic random-bucket controls are not promotable. If either passes, the interpretation must be red-teamed before any positive claim because it may indicate over-permissive variables or accidental toy-scale interpolation.

## Success criterion
Primary success requires a non-control representation with:

- target labels no more permissive than public fingerprint or x-only Kummer class;
- a consistent full matrix;
- positive factor-component rank;
- at least one factor key spanning multiple forms;
- fewer factor labels than the per-form control; and
- no failed positive-control gate.

This would be a viable relation-generation/index-calculus precursor only. It would not by itself prove sparse linear algebra closure, target descent, asymptotic scaling, or a faster-than-rho ECDLP algorithm.

## Falsification criterion
If no primary model satisfies the success criterion, the tested relation-object merge family is scoped negative. Diagnostic local coherence may still be preserved as a next-step clue, but the next positive search must extract better public factor labels or use a different algebraic backend before quotient pooling.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1032_p231_relation_generation_representation_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1032_p231_relation_generation_representation_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1032_p231_relation_generation_representation_audit_probe.json
```

## Interpretation boundary
This is an index-calculus precursor experiment. A positive result would identify a reusable relation-object representation to optimize later, not a deployed or asymptotic break. Pollard rho remains the one-target scalar-search baseline.

## Results
- timestamp: 2026-06-30T02:50:09Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1032_p231_relation_generation_representation_audit.py --contract ecdlp_index_calculus_state/experiment_contract_p1032_p231_relation_generation_representation_audit.md --out ecdlp_index_calculus_state/low_term_total2_p1032_p231_relation_generation_representation_audit_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1032_p231_relation_generation_representation_audit_probe.json`
- claim: `P1032_DIAGNOSTIC_LOCAL_RELATION_OBJECT_SIGNAL_ONLY`
- positive controls:
  - leaf `[19]`: `control_form_factor_public_target` rank/augmented `26/26`, consistent.
  - leaf `[8]`: `control_form_factor_public_target` rank/augmented `16/16`, consistent.
- primary promoted relation-object merge models: `0`.
- diagnostic local relation-object models: `2`, both in leaf `[8]`.
- leaf `[19]`:
  - `17` selected rows, `3` fresh positives, `0` fresh false rows, `26` unique pre-elimination forms, factor count `16`.
  - global factor/public target control rank/augmented `11/12`, inconsistent.
  - public-slice and Kummer-x factor labels rank/augmented `20/21`, inconsistent.
  - row-key and salt-pair factor labels with public target rank/augmented `23/24`, inconsistent.
  - diagnostic row-key/salt-pair target labels also remain inconsistent at `24/25`.
- leaf `[8]`:
  - `12` selected rows, `3` fresh positives, `1` fresh false row, `16` unique pre-elimination forms, factor count `16`.
  - global factor/public target control rank/augmented `8/9`, inconsistent.
  - public-slice and Kummer-x factor labels rank/augmented `12/13`, inconsistent.
  - row-key and salt-pair factor labels with public target rank/augmented `15/16`, inconsistent.
  - diagnostic row-key and salt-pair factor+target labels are consistent at `16/16`, with factor-label compression ratios `0.5625`.

## Interpretation
OBSERVATION / DIAGNOSTIC ONLY: leaf `[8]` has local row-key/salt-pair coherence when the target variable is also local to that row/salt object, but no tested representation shares the target by public or Kummer x-coordinate while preserving consistency. This is not a promotable factor-base representation yet.

NEGATIVE RESULT under the tested primary catalog: public-slice, Kummer-x, row-key, salt-pair, support-pattern, split-slice, global, and deterministic random-bucket factor labels all leave an augmented-rank gap when the target variable is shared by public. The obstruction has moved earlier than RHS normalization: we need a factor-label extraction rule that can merge forms without making the target variable local.

## Next concrete action
Create P1033 as a factor-label extraction scout for leaf `[8]`: derive public row/salt/local-factor fingerprints from the verifier form metadata and test whether any fingerprint can merge at least two forms while keeping the target variable public-shared and the pre-elimination matrix consistent.
