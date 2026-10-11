# Explicit degree-four root-count design audit

## Audit basis

- Idea: `IDEA-20261006-576825`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `RQ-ECDLP-4fcbd3`, `KR-RHO-13bf67`, and the finite
  polynomial/representation controls.

## Scientific boundary

This proposal is unusually well-bounded as a deterministic finite control:
the two polynomials, field, distinct-root convention, exhaustive scan,
`x^4` control, and interpretation limits are explicit. Its strongest output
is the pair of exact root counts. A root need not lift to a rational point on
the corresponding curve, and a root-count difference is not evidence of a
torsion transfer or an ECDLP method.

## Load-bearing repairs

1. Make the field implementation auditable. Record the prime certificate for
   `1031`, the field-element encoding and iteration order, and an independent
   evaluation implementation. The exhaustive scan should produce a machine-
   readable list of roots, not only two counters.
2. Recompute the curve cells independently. Record the exact short-
   Weierstrass discriminant convention, nonsingularity residues, and the
   coefficient-to-polynomial map. Keep the polynomial root count separate from
   the set of x-coordinates that lift to affine curve points, as the proposal
   correctly notes.
3. Bind the control semantics. Verify that `x^4` has exactly one distinct
   root and that every reported root of both test polynomials evaluates to
   zero. Check the leading coefficient and reject degree-drop cells before
   interpreting the counts.
4. Preserve the existential scope. The claim is about these two frozen
   polynomials over one field. If a broader pattern is desired, define a
   coefficient-family sampling rule and a multiple-comparison policy before
   looking at results; do not add a third value of `B` after seeing equality.
5. Keep the cost and interpretation record complete. Record scan operations,
   timing, and memory only as finite-control observations. Do not turn a root
   count into a point relation, factor-base yield, or DLP claim without a
   separate map and known-answer certificate.
6. Complete the execution contract before approval. The proposal needs an
   exact implementation path, source/input hash, stdout/stderr and raw result
   paths, deterministic seed policy if any, and an artifact/archive handoff.
   Those are ordinary readiness obligations even though the arithmetic test
   itself is small.

## Readiness and disposition

The arithmetic specification is nearly complete and appears suitable for a
small deterministic control once converted into an executable experiment
contract. The remaining work is implementation/archive binding, independent
field evaluation, and preserving the strict finite interpretation.

Disposition: **retain proposed as a candidate finite root-count control; do
not approve or dispatch the idea record itself.** Convert it to a complete
ready experiment with the exact command, artifacts, independent evaluator,
and archive handoff, then recheck capacity and selector admission.
