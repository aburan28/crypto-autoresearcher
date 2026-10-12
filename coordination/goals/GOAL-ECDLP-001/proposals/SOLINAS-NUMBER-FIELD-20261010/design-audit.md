# Solinas number-field root-discriminant audit

## Audit basis

- Idea: `IDEA-20261009-b6d31b`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `EXP-ECDLP-3e8403`, `KR-IC-cd159a`, `H-ECDLP-bd1572`, and
  the number-field lifting obstruction in `KN-TECH-06bb4e`.

## Scientific boundary

The proposed question—whether the particular number fields used for Solinas
moduli give elliptic lifts more useful points than matched fields—is a finite
number-field comparison. Small root discriminant is a field invariant, not a
direct certificate of Mordell-Weil rank, point height, or useful reduction
coverage. The current record does not yet isolate that variable or define a
reproducible coverage experiment.

## Load-bearing repairs

1. Certify every field input. For each polynomial `f`, record irreducibility,
   degree, signature, discriminant of the polynomial order, index of
   `Z[t]` in the maximal order, maximal-order discriminant and root
   discriminant. A low-weight polynomial need not define a field with the
   claimed root-discriminant advantage.
2. Certify the reduction prime. Require `p=f(2^k)` to be prime, specify the
   degree-one prime of the maximal order above `p`, its residue map, and any
   ramification or index exceptions. The phrase “toy `f(2^k)` primes” needs a
   deterministic primality-filtered panel; `k=4..12` alone does not ensure a
   usable prime or a comparable panel for each NIST shape.
3. Match the comparison design. Root discriminant, degree, signature, field
   discriminant, `p`, curve model, and reduction prime are not independent in
   the current sampling plan. Random fields must be matched or stratified on
   degree, coefficient/height budget, signature, discriminant band, and the
   existence of a degree-one prime of the same norm. Otherwise a regression
   can report a field-size or degree effect as a discriminant effect.
4. Bind the elliptic-curve family and reduction map. Specify the curve over
   `Q` or the base field, good-reduction certificate, its rational rank and
   torsion, the subgroup at the degree-one prime, and the exact map
   `E(K_f) -> E(F_p)`. Report rank lower bounds from exhibited points separately
   from certified rank and descent upper bounds; degree-12 descent failure is
   an inconclusive cell, not a null result.
5. Define the height and coverage observable. State the canonical-height
   normalization, the meaning of `20 log p`, whether points are counted with
   multiplicity or modulo torsion/sign, the target set or target distribution,
   and whether coverage means distinct residues, subgroup span, relation rank,
   or successful target decomposition. Point counts alone do not measure a
   usable lift.
6. Charge construction and factorization costs. Include field construction,
   maximal-order computation, class/unit data, descent, point enumeration,
   reduction, deduplication, and target verification. A small discriminant can
   reduce one arithmetic cost while increasing another; the claim cannot be
   based solely on the number of points found.
7. Replace the global regression with preregistered contrasts. Compare the
   Solinas family to same-degree, same-`p` or tightly matched random fields,
   use independent curves/targets, and predeclare the bootstrap unit and
   multiple-cell correction. The stated `>0.2` coverage-exponent threshold
   needs a fit range, uncertainty model, and at least one unseen target per
   cell.
8. Keep the interpretation finite. A coverage or rank difference would be a
   result for the measured field/curve panel. It would not show that a Solinas
   shape improves ECDLP asymptotics or that root discriminant alone controls
   elliptic lifts.

## Readiness and disposition

The record is proposal-only and has no committed implementation, field
certificate bundle, target panel, or executable descent contract. Its claimed
random-field control is not matched on the variables needed for attribution.

Disposition: **retain proposed as a conditional number-field comparison; do
not approve or dispatch as filed.** Repair the maximal-order/prime
certificates, matched-field design, curve and height definitions, coverage
metric, and complete cost accounting. Recheck dependencies, runnable state,
and approval capacity after a complete contract exists.
