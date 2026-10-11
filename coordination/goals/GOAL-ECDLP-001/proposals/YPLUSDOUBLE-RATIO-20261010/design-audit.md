# `y(P)+y(2P)` image-ratio design audit

## Audit basis

- Idea: `IDEA-20261007-dc7612`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-623a32`, `KR-RHO-13bf67`, and the separate
  x-plus-double image controls.

## Scientific boundary

This is a finite image-size ratio for a y-coordinate expression on one small
curve. The proposal correctly excludes undefined y-values and treats the
constant and y-image checks as instrument controls. Its main requirement is to
make the exceptional doubled points and point-level image artifacts explicit;
the ratio is not an attack-stage or ECDLP result.

## Load-bearing repairs

1. Certify the field and curve. Record primality of 41, the exact
   discriminant convention/residue, every affine point, the point at infinity,
   and all `y=0` points. Verify the complete point list independently.
2. Define the domain exactly. State how `y(P)=0`, `2P=O`, and `y(2P)=0` are
   excluded, report each exclusion category, and emit the final ordered set
   `D`. Do not silently drop a point because the doubling implementation
   failed; distinguish mathematical exceptions from implementation failures.
3. Verify doubling and y signs. Compute complete `[2]P` using the duplication
   formula and `P+P`, check the y-coordinate sign as well as x, and verify
   `s(-P)=-s(P)` on the retained domain. Emit per-point `(P,2P,s(P))`
   records and the distinct image set.
4. Define the controls precisely. The constant-zero control should be run on
   the same ordered domain and return image size one; the y-image control must
   use the same domain and report its exact size, with a void rule if `|D|`
   itself is too small for the stated lower bound.
5. Preserve the finite threshold. `|s(D)|/|D| >= 1/4` is a one-curve
   observation. The random-function expectation is only context and does not
   prove the threshold; broader claims require a preregistered curve/prime
   panel and uncertainty treatment.
6. Complete execution/archive binding. Freeze the exact command, source/input
   hashes, raw point/domain/image artifacts, independent evaluator, and
   archive handoff before approval.

## Readiness and disposition

The proposal is close to a ready finite control. Its remaining obligations are
complete exceptional-point accounting, full-point doubling verification, and
replayable control/image artifacts.

Disposition: **retain proposed as a candidate y-plus-double image-ratio
control; do not approve or dispatch the idea record itself.** Convert it to a
complete ready experiment with exact domain and artifact binding, then
recheck capacity and selector admission.
