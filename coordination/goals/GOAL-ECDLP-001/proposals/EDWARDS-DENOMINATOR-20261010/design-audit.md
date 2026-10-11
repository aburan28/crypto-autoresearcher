# Edwards denominator control audit

## Audit basis

- Idea: `IDEA-20261006-8aedbe`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Adjacent contracts: `EXP-REP-001` and `EXP-MODEL-4159eb`, which already
  measure Edwards/Weierstrass representation and solving-degree effects.

## Scientific boundary and overlap

The proposed measurement enumerates affine points on two selected Edwards
models over `F_41` and counts ordered pairs for which either standard affine
addition denominator vanishes. Its distinct contribution is a small exact
completeness/incompleteness fixture for the chosen parameters. It does not
measure a discrete-log cost, factor-base decomposition, inversion batching,
or rho step improvement.

The existing representation contracts already cover the relevant model-level
ECDLP question at substantially broader parameter ranges. This proposal
should therefore be attached as a denominator-domain preflight or kept as a
standalone arithmetic control; it should not be presented as a new model
attack or as evidence that a parameter character changes the ECDLP exponent.

## Load-bearing contract requirements

The parameter-selection rule must be frozen exactly. Record every candidate
`d` in the scan, its Legendre symbol, its affine point count, and the reason
for rejection. The selected `d_ns` and `d_sq` are chosen by a point-count
threshold, not by the denominator outcome, and the same rule must be applied
before either denominator census is inspected.

For every ordered pair, including repeated points, record the two denominator
values separately before taking their union. Bind the field representation,
the Edwards equation, the exact affine addition formulas, and the convention
for a zero denominator. A pair with a zero in both denominators must count
once in `Z`, while the two raw zero indicators remain available for audit.
Every pair must pass an independent on-curve check; a point-set mismatch
invalidates the census rather than reducing the denominator count.

The second nonsquare control is important because one nonsquare parameter
with zero rational denominator pairs does not establish a parameter-class
law. Its selection, point-count gate, and missing-parameter outcome must be
recorded before scoring. The `d=0` replacement is a different curve and may
only be a diagnostic; it cannot serve as a same-curve null.

The square arm is a concrete positive-control prediction, not a theorem
implied by “square” alone. The repair must state that `Z_sq >= 1` is tested
for the selected parameter and that failure is a finite negative for this
selection, not evidence that all square parameters have complete or
incomplete affine addition. If the denominator locus is rational only over an
extension, a zero `Z_sq` remains a valid finite observation under the stated
base-field scope.

## Interpretation and disposition

The strongest result is an exact pair count for two selected Edwards curves
and the associated controls. A zero count on the nonsquare arm is not a
proof for every prime or every nonsquare parameter, and a positive square-arm
count is not a cryptanalytic advantage. Any completeness statement beyond
the enumerated field requires an independently verified theorem; the recalled
reference in the proposal is not support until retrieved and checked.

Disposition: **keep proposed as a control; do not approve it as an independent
ECDLP experiment as filed.** Repair the parameter-selection receipt, separate
the two denominator indicators, and bind all point/order/curve certificates.
If retained, place it before the existing representation experiment as a
correctness gate. Otherwise leave it unexecuted under the current empty
selector and resource guard.
