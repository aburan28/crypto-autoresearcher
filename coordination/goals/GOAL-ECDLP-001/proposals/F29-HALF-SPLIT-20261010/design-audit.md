# F29 lower-half x-count design audit

## Audit basis

- Idea: `IDEA-20261006-43905e`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.

## Scientific boundary

The proposal is an exact census of affine points on two named short
Weierstrass curves over `F_29`, split by the fixed residue sets
`{0,...,14}` and `{15,...,28}`. It retains x-coordinate multiplicity from
the number of square roots and uses a repeated count, a projective total, and
a singular-model refusal as controls.

This is a finite coordinate-count fixture, not point halving, a rho step, a
factor-base decomposition, or a discrete-log distinguisher. The fact that the
two curves have different lower/upper counts does not identify a scalar
character or provide a way to recover a logarithm.

## Correctness and statistical limits

The exact claim is reproducible if the cut, field representation, curve
coefficients, affine/projective convention, and handling of y=0 are frozen.
Every x value must be checked by the quadratic-character rule or an
independent enumeration path. The self-count must reproduce the same curve,
and the projective total must equal the affine total plus the point at
infinity. A mismatch is a scanner or specification defect until resolved.

The lower and upper sets have different cardinalities, so neither individual
imbalance is a deviation from an exactly balanced uniform baseline. The
proposed cross-curve absolute-gap comparison is a descriptive difference
between two selected curves at one prime and one cut, not a calibrated test
of a population effect. Any stronger statistical interpretation would need a
preregistered curve family, selection rule, and null distribution.

The choice of the two curves and the cut is fixed by the proposal, but the
result remains conditional on those choices. It should not be generalized to
other curves, primes, coordinates, or scalar distributions without new
controls. The cited binary point-halving frontier is a different mechanism;
the F29 count does not alter the generic square-root baseline.

## Claim ceiling and disposition

A successful recount can certify only the four finite half-counts, the two
imbalances, their absolute difference, the self-count, and the projective
totals. It cannot establish a useful representation, an ECDLP speedup, a rho
step-cost change, or a transferable coordinate bias. A failed premise or
singular refusal is an invalid/infrastructure outcome, not evidence against a
broader ECDLP hypothesis.

Disposition: **keep proposed as a low-cost correctness or descriptive
measurement; do not approve it as an independent attack experiment.** It may
be attached to a later coordinate-statistics study only if that study defines
a family-level null and a scalar-relevance test. Otherwise the finite census
does not justify execution under the current empty selector and machine-load
conditions.

Next action: preserve the exact recount contract, including the self-count and
projective checks, and either attach it as a preflight fixture or leave it as
an unexecuted proposed control. Do not promote the count gap as cryptanalytic
evidence.
