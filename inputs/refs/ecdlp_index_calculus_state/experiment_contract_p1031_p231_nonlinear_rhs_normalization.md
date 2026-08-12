# Experiment Contract: P1031 p231 nonlinear RHS-normalization audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1030 linear-lift obstruction may be caused by using only affine q/salt/public coordinates. Nonlinear quotient-ratio, public rational/Kummer-like, salt-quadratic, character, or support-moment features may normalize RHS offsets so that the remaining target-eliminated rows become a consistent reusable factor relation system.

## Null hypothesis
All tested nonlinear feature maps either leave the augmented-rank gap, fit only by interpolation without held-out public prediction, or depend on lossy/support-only diagnostics that do not produce a promotable factor-bank representation.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scopes:
  - reference leaf `[19]` selected by P1022, row-signature compressed
  - neighbor leaf `[8]` selected by P1029, row-signature compressed
- source windows:
  - training: P1022 positive calibration plus validation through `12432_12439`
  - negative controls: `12224_12231`, `12264_12271`, `12320_12327`
  - fresh: `12440_12447` through `12496_12503`
- quotient method: same-public form pairs eliminate the target coefficient as `q_right * left - q_left * right`
- modulus/order: `11779`
- nonlinear feature catalogs:
  - quotient ratios and powers;
  - public quadratic/rational coordinates;
  - Kummer-like public sign quotient coordinates;
  - salt quadratic and quotient-salt interactions;
  - Legendre/character features;
  - support moments as diagnostic-only coordinates.

## Metrics
- selected row count, fresh positive count, and fresh false count per scope
- baseline factor rank and augmented rank
- nonlinear lifted matrix rank and augmented rank
- context rank and factor-component rank
- held-out public tested/passed/skipped counts
- repeated-coefficient RHS-normalizer exactness and leave-one-public-out behavior
- primary promoted nonlinear model count
- diagnostic-only model count

## Positive control
The baseline factor-only matrix must reproduce P1030:

- leaf `[19]`: quotient rank/augmented `2/3`
- leaf `[8]`: quotient rank/augmented `2/3`

## Negative control
A nonlinear map is not promotable if it:

- selects false rows in the scope without preserving that noise flag;
- has no held-out public rows tested;
- fails any tested held-out public row;
- is support-dependent diagnostic-only;
- fits only by adding enough columns to interpolate observed rows; or
- leaves the full lifted matrix inconsistent.

## Success criterion
Primary success requires a predictive nonlinear lifted model or repeated-coefficient RHS normalizer with:

- full matrix consistency;
- positive factor-component rank;
- at least one held-out public row tested;
- all tested held-out public rows passed; and
- zero failed control gates.

## Falsification criterion
If no predictive nonlinear feature map satisfies the success criterion and any exact fits are diagnostic-only or held-out-untested, this is a scoped negative for the tested nonlinear RHS-normalization family. The next search should then move to nonlinear relation generation itself, such as bivariate factor/slice backends or a new relation object, rather than RHS repair after target elimination.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1031_p231_nonlinear_rhs_normalization.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1031_p231_nonlinear_rhs_normalization.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1031_p231_nonlinear_rhs_normalization_probe.json
```

## Interpretation boundary
This is an index-calculus precursor experiment. A positive result would be a toy nonlinear normalization signal, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-30T02:35:56Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1031_p231_nonlinear_rhs_normalization.py --contract ecdlp_index_calculus_state/experiment_contract_p1031_p231_nonlinear_rhs_normalization.md --out ecdlp_index_calculus_state/low_term_total2_p1031_p231_nonlinear_rhs_normalization_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1031_p231_nonlinear_rhs_normalization_probe.json`
- claim: `NEGATIVE_RESULT_P1031_NONLINEAR_RHS_NORMALIZERS_NO_PROMOTION`
- leaf `[19]` baseline: `17` selected rows, `3` fresh positives, `0` fresh false rows, `37` quotient relations, rank/augmented `2/3`, inconsistent.
- leaf `[8]` baseline: `12` selected rows, `3` fresh positives, `1` fresh false row, `26` quotient relations, rank/augmented `2/3`, inconsistent.
- nonlinear lifted models tested: `q_ratio_power`, `public_quadratic`, `public_rational_kummer`, `salt_quadratic`, `q_salt_nonlinear`, `q_public_quadratic`, `character_features`, and diagnostic `support_moments_diagnostic`.
- promoted lifted models: `0`.
- diagnostic lifted models: `0`.
- repeated-coefficient RHS normalizer clusters tested: `16` in each scope.
- viable repeated-coefficient RHS normalizers: `0`.
- exact-but-nonpredictive cluster fits:
  - leaf `[19]`: `3` exact cluster fits; all leave-one-public-out results were `0` passes (`q_ratio_power` on `10` samples over `5` publics; `q_ratio_power` on `8` samples over `4` publics; `q_salt_nonlinear` on `8` samples over `4` publics).
  - leaf `[8]`: `7` exact two-sample/two-public cluster fits; all leave-one-public-out results were `0/2`.

## Interpretation
NEGATIVE RESULT: the tested nonlinear feature catalog does not repair the P1030 augmented-rank gap. Some repeated-coefficient clusters can be fit exactly, but those fits fail held-out public prediction, so they are interpolation artifacts rather than reusable RHS normalizers.

This narrows the current branch further: simple nonlinear RHS normalization after target elimination is not enough for leaf `[19]` or leaf `[8]`. The next positive search should change relation generation or the algebraic object before target elimination, rather than fitting offsets after quotient rows already exist.

## Next concrete action
Create P1032 as a relation-generation representation audit: test bivariate factor/slice identities or Kummer/sign-quotient relation objects before quotient pooling, with a positive-control surface where the slice identity is known to preserve roots and a negative-control random slice.
