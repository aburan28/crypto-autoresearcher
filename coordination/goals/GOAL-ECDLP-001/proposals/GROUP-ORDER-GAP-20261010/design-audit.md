# Paired group-order gap audit

## Audit basis

- Idea: `IDEA-20261006-b8d10a`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Governing records: `KR-RHO-755e35`, `KR-RHO-13bf67`, and
  `KR-RHO-53c89f`.

## Scientific boundary

The proposal asks for an exact finite census: find the least prime in a
declared interval at which two named short-Weierstrass curves are nonsingular
and ordinary, then compare their point counts. This is a low-cost arithmetic
measurement, not an ECDLP attack, isogeny construction, embedding-degree
test, or rho experiment.

For curves over the same finite field, an unequal point count is consistent
with the finite-field isogeny criterion: curves in the same finite-field
isogeny class have the same Frobenius trace and order. The result must be
phrased with that scope. It does not say that every pair of models with
different coefficients is non-isogenous over every field, nor does it imply
that either curve has a weak discrete-log representation.

## Exact-count contract

The prime scan must be deterministic and occur before either order is
inspected. Record every candidate prime, both discriminant residues, both
point counts, both traces, and the precise reason for exclusion. “Ordinary”
must be evaluated from the trace under the stated characteristic range;
trace zero or any other supersingular case must not pass the gate.

At the selected prime, independently count both curves, include the point at
infinity exactly once, and retain an independent self-count of `E0`. A
disagreement in the self-count invalidates the counting instrument rather
than serving as a group-order equality or inequality. The implementation
must bind the prime-primality test, field arithmetic, nonsingularity test,
and the full point-count method in the manifest.

The empty interval is a valid finite outcome of the declared search and must
not be replaced by a later prime. Likewise, equal orders at the least
eligible prime falsify only this proposal’s prediction; equality alone is not
a proof that an isogeny has been constructed or that a transfer is useful.

## Interpretation and disposition

The strongest result is the recorded prime, two exact orders, two traces, and
their integer difference for the specified curves and interval. It has zero
ECDLP exponent delta and does not test anomalous curves, small embedding
degree, smooth orders, or any endomorphism transfer. Any such interpretation
would require a separate contract with its own certificates and cost model.

Disposition: **keep proposed as a low-cost finite point-count measurement; do
not approve it as an independent cryptanalytic experiment.** It can be
attached as a sanity/control row to the existing `RQ-ECDLP-165d4b` census
work if that row is needed, but it should not generate a second isogeny or
weak-curve direction from one order comparison. Leave it unexecuted while the
selector has no admitted row and the resource guard remains unfavorable.
