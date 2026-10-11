# Tangent-intercept image-size design audit

## Audit basis

- Idea: `IDEA-20261007-7091a3`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the tangent/slope
  image controls.

## Scientific boundary

This is a finite image-size comparison of tangent slopes and two intercept
maps on one small curve. It is not an attack-stage cost or ECDLP claim. The
proposal has a sensible same-point shift control, but both predictions leave
outcome gaps: the first accepts a difference of at least 3 while falsifying
below 3, and the second accepts at most 1 while falsifying at least 3. Results
in the intervening values need an explicit inconclusive disposition.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 13, the exact
   discriminant convention/residue, every affine point, the `y=0` exclusion,
   and the point-at-infinity handling. Verify all points independently before
   constructing images.
2. Freeze tangent arithmetic. Define the field representative, inverse of
   `2y`, slope-zero handling, and exact formulas for `mu` and `mu_shift`.
   Emit per-point `(x,y,lambda,mu,mu_shift)` records so image sets can be
   replayed and independently checked.
3. Repair the decision partition. Predeclare support for the first prediction
   when `N_lambda-N_mu >= 3`, falsification when it is below 3, and no gap is
   present there. For the shift arm, use support for `<=1`, falsification for
   `>=3`, and classify the value `2` as inconclusive rather than assigning it
   to either side.
4. Explain the control’s comparison target. The shift changes the slope
   coefficient at the same points; it is a finite algebraic null, not a random
   or group-action null. If a distributional interpretation is desired,
   specify additional random affine-function controls before observing the
   image sizes.
5. Keep the finite interpretation literal. A smaller image can indicate a
   many-to-one coordinate map at `p=13`, but it does not make the map a factor
   base, relation source, or inversion. Any such use requires separate
   membership, precomputation, relation, and rho-cost accounting.
6. Complete execution/archive binding. Freeze the exact command, source/input
   hashes, raw point/image artifacts, independent evaluator, and archive
   handoff before approval. A small exhaustive image census still needs a
   replayable record.

## Readiness and disposition

The proposal is close to a ready finite control, with the decision gaps and
per-point image artifacts as its main repairs.

Disposition: **retain proposed as a candidate tangent-intercept control; do
not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with explicit three-way outcomes and replayable artifacts,
then recheck capacity and selector admission.
