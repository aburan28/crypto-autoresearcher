# Canonical-point chord-slope image design audit

## Audit basis

- Idea: `IDEA-20261007-fd7c23`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the finite
  tangent/intercept image controls.

## Scientific boundary

This is a finite image comparison for chords from one canonically selected
point. The slope image and the arithmetic-index label image are clearly
separated, and the proposal makes no ECDLP claim. The main contract gap is the
label null: enumeration index modulo 19 is not distribution-free unless the
point ordering is frozen and, if intended, independently randomized. The
second prediction also leaves an intermediate outcome interval.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 19, the exact
   discriminant convention/residue, every affine point, and the point list
   used to select `Q`. Verify the chosen point and its nonzero-y condition
   independently.
2. Define the eligible domain. State how all points with `x(P)=x(Q)` are
   excluded, including both signs and any y-zero point, and emit the exact
   ordered `E_set`. Verify every denominator and slope in the field.
3. Verify the chord implementation. Compute each slope by the displayed
   formula and an independent complete chord implementation, compare the
   result, and emit per-point `(P,Q,s(P))` records plus the distinct image.
4. Freeze the label control. Define the point enumeration order and index
   mapping precisely. If the control is meant to test order artifacts, add
   independent random permutations with fixed seeds and report their image
   distribution; one arbitrary index assignment is only a single finite null.
5. Repair the decision partition. The first arm has a complete threshold at
   `n-N_s=4`. The label arm predicts `n-N_lab<=1` but falsifies only at
   `n-N_lab>=4`; values 2 or 3 must be recorded as inconclusive rather than
   forced into either outcome.
6. Preserve the finite interpretation and archive binding. A slope-image gap
   at `p=19` is not a factor base, summation polynomial, or ECDLP advantage.
   Before approval, freeze the exact command, source/input hashes, raw point/
   image artifacts, label permutations, independent evaluator, and archive
   handoff.

## Readiness and disposition

The proposal is close to a ready finite control. Its remaining requirements
are canonical-point/domain certificates, a defined label null, explicit
inconclusive handling for the label arm, and replayable artifacts.

Disposition: **retain proposed as a candidate canonical chord-slope control;
do not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with the exact label null and artifact paths, then recheck
capacity and selector admission.
