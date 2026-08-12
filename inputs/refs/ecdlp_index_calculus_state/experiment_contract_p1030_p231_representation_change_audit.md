# Experiment Contract: P1030 p231 representation-change audit

## Hypothesis
HYPOTHESIS / TOY-EVIDENCE: the P1028/P1029 augmented-rank obstruction may be representation-specific. A quotient-normalized or projected representation of the same target-eliminated rows may expose a consistent factor relation signal that the raw leaf-coordinate basis hides.

## Null hypothesis
Invertible factor-coordinate changes preserve the inconsistency, non-injective projections only create lossy diagnostics, and quotient-normalized q/salt/public lifts fail held-out public prediction. Then the current total-2 motif branch should move to a genuinely nonlinear or different-coordinate representation rather than more linear bookkeeping.

## Parameters
- field/curve family: toy p231 ECDLP harness, target `22050.cf1@11731`
- scopes:
  - reference leaf `[19]` selected by the P1022 rule, row-signature compressed
  - neighbor leaf `[8]` selected by the P1029 relaxed scout, row-signature compressed
- windows:
  - training: P1022 positive calibration plus validation through `12432_12439`
  - negative controls: `12224_12231`, `12264_12271`, `12320_12327`
  - fresh: `12440_12447` through `12496_12503`
- quotient method: same-public form pairs eliminate the target coefficient as `q_right * left - q_left * right`
- modulus/order: `11779`
- baseline: Pollard rho remains the one-target scalar baseline; this audit measures relation precursor structure only

## Metrics
- selected row counts and false-row counts per scope
- reconstructed form count and reconstruction errors
- target-eliminated relation count
- factor-only coefficient rank, augmented rank, and consistency
- invertible-coordinate control rank/consistency
- non-injective projection rank/consistency and held-out public checks
- quotient-normalized lifted-model rank/consistency and held-out public checks
- primary promoted model count
- diagnostic projection count

## Positive control
The audit must reproduce the known row-signature-compressed obstruction:

- leaf `[19]`: raw factor rank/augmented `2/3`
- leaf `[8]`: raw factor rank/augmented `2/3`

Invertible factor-coordinate controls must preserve those ranks and inconsistency.

## Negative control
A representation is not promotable if it:

- uses selected false rows without flagging the scope as noisy;
- is a non-injective projection that cannot lift back to the full factor relation space;
- has no held-out public rows tested;
- fails held-out public rowspace prediction; or
- succeeds only by adding enough nonpredictive context columns to interpolate observed publics.

## Success criterion
Primary success requires a predictive quotient-normalized lifted model with:

- matrix consistency;
- positive factor-component rank after accounting for context rank;
- at least one held-out public row tested;
- all tested held-out public rows passing; and
- no failed positive-control or negative-control gate.

## Falsification criterion
If all invertible controls preserve inconsistency and no predictive lifted model satisfies the success criterion, this is a scoped negative for the tested linear representation changes. Diagnostic projections may remain useful only if they define a concrete next nonlinear representation to test.

## Reproduction command
```bash
PYTHONPATH=tasks/ecdlp_index_calculus \
  python3 tasks/ecdlp_index_calculus/low_term_total2_p1030_p231_representation_change_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1030_p231_representation_change_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1030_p231_representation_change_audit_probe.json
```

## Interpretation boundary
This is an index-calculus precursor experiment. A positive result would be a toy representation signal, not sparse linear algebra closure, target descent, asymptotic evidence, or a deployed faster-than-rho ECDLP solver.

## Results
- timestamp: 2026-06-30T02:27:25Z
- command: `PYTHONPATH=tasks/ecdlp_index_calculus python3 tasks/ecdlp_index_calculus/low_term_total2_p1030_p231_representation_change_audit.py --contract ecdlp_index_calculus_state/experiment_contract_p1030_p231_representation_change_audit.md --out ecdlp_index_calculus_state/low_term_total2_p1030_p231_representation_change_audit_probe.json`
- output artifact: `ecdlp_index_calculus_state/low_term_total2_p1030_p231_representation_change_audit_probe.json`
- claim: `NEGATIVE_RESULT_P1030_LINEAR_REPRESENTATION_CHANGES_NO_PROMOTION`
- reference leaf `[19]`: `17` selected rows, `3` fresh positives, `0` fresh false rows, `37` compressed quotient relations, factor rank/augmented `2/3`, inconsistent.
- neighbor leaf `[8]`: `12` selected rows, `3` fresh positives, `1` fresh false row, `26` compressed quotient relations, factor rank/augmented `2/3`, inconsistent.
- invertible coordinate controls: preserved rank and inconsistency for both scopes.
- lifted quotient models tested: `factor_only`, `scaled_q_pair`, `scaled_q_symmetric`, `scaled_public_xy`, `scaled_salt_minmax_gap`, `scaled_q_salt_interaction`, and `scaled_q_public_interaction`.
- primary promoted lifted models: `0`.
- diagnostic non-injective projections: `0`.
- leaf `[19]` lifted rank pattern: `factor_only` `2/3`; `scaled_q_pair` `3/4`; `scaled_q_symmetric` `4/5`; `scaled_public_xy` `5/6`; `scaled_salt_minmax_gap` `5/6`; `scaled_q_salt_interaction` `5/6`; `scaled_q_public_interaction` `6/7`. Every tested lift remains inconsistent.
- leaf `[8]` lifted rank pattern: `factor_only` `2/3`; `scaled_q_pair` `3/4`; `scaled_q_symmetric` `4/5`; `scaled_public_xy` `5/6`; `scaled_salt_minmax_gap` `5/6`; `scaled_q_salt_interaction` `5/6`; `scaled_q_public_interaction` `6/7`. Every tested lift remains inconsistent.

## Interpretation
NEGATIVE RESULT / RESTRICTED THEOREM CONTROL: invertible linear factor-coordinate changes preserve coefficient and augmented ranks, as expected, so they cannot repair the P1028/P1029 obstruction. The tested quotient-normalized q/salt/public lifts add columns but do not close the augmented-rank gap; each rank increase is matched by an augmented-rank increase.

This narrows the current branch: linear coordinate changes, low-dimensional quotient lifts, and lossy column projections do not yield a promotable factor-bank representation for the row-signature-compressed leaf `[19]` or leaf `[8]` scopes. It does not rule out index calculus. It says the next positive move needs a genuinely different representation, such as nonlinear RHS normalization, a bivariate quotient/factor backend, or a relation object that changes the algebra before target elimination.

## Next concrete action
Create P1031 as a nonlinear representation audit. Candidate directions: quotient-ratio invariants, bivariate factor/slice identities, Kummer/sign quotient coordinates, or a learned-but-held-out nonlinear RHS normalizer. The first gate should require held-out public prediction and must compare against the P1030 linear-lift negative.
