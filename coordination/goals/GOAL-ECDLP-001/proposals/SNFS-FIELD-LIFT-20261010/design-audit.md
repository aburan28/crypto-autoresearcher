# SNFS-field lift design audit

## Audit basis

- Idea: `IDEA-20261009-4b1724`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `H-ECDLP-bd1572`, `EXP-ECDLP-3e8403`, `KR-IC-cd159a`,
  `KN-TECH-06bb4e`, and the number-field lifting controls.

## Scientific boundary

The proposed comparison asks whether a number field selected for a special-
prime representation changes rank, heights, or reduction coverage for a
fixed elliptic curve. That is a valid finite control, but the current record
assumes a degree-one reduction prime and treats partial descent output as a
complete Mordell--Weil inventory. The field construction, prime ideal, rank
meaning, and coverage observable must be fixed before a comparison with random
fields is interpretable.

## Load-bearing repairs

1. Certify the field and the prime ideal. For each `p`, `d`, and `c`, record
   the irreducible factor defining `K`, the maximal order, discriminant,
   index, signature, and the exact prime ideal above `p`. A degree-one prime
   exists only when the defining polynomial has a linear factor modulo `p`;
   the asserted map `alpha -> 2^(n/d)` needs `d | n` or a separately
   certified element of `F_p` whose `d`th power is `c`. Otherwise the
   reduction is to an extension residue field, not `F_p`.
2. Bind the curve reduction map. Record a minimal integral model over `K`,
   good reduction at the selected prime, the residue map, the target subgroup
   in `E(F_p)`, and the cofactor/order certificate. Verify that the reduced
   K-points are in the intended subgroup and that target decompositions can be
   checked independently.
3. Define the rank observable. Since `E(Q)` embeds into `E(K)`, the rank gain
   is nonnegative, but descent generally returns lower and upper bounds with
   unresolved Tate--Shafarevich or saturation issues. Report rank intervals,
   exhibited independent points, height-pairing determinants, and the
   certification status; do not average censored lower bounds as exact rank
   gains.
4. Make the random-field control matched. Match degree, maximal-order
   discriminant/root discriminant, signature, ramification at `p`, existence
   of a degree-one prime, residue map, and field arithmetic representation.
   A random polynomial with similar discriminant but no usable prime ideal is
   not a control for the SNFS field.
5. Define canonical height and “new point.” State the normalization from
   `K`, the torsion quotient, local height decomposition, model dependence,
   and whether a point is new modulo `E(Q)` or merely a different expression
   of an old point. Give saturation and basis-completeness checks before
   interpreting the minimum height.
6. Distinguish an enumerated subset from all bounded-height points. If the
   descent supplies only a subgroup or a coefficient box, coverage is a
   lower bound on the image of the enumerated points. Report per-field point
   count, distinct reduction image, union image, subgroup order, collision
   rate, and target-hit/decomposition certificates. The union over fifteen
   fields is a sample statistic, not a statement about every SNFS field.
7. Predeclare the scale and censoring model. Explain the allowed `n`, why
   degree five stops at 24, how singular/nonprime cases are filtered, and how
   failure to complete a cubic or quintic descent is recorded. Two or three
   degrees and five primes cannot establish a height constant `c` without a
   fit range, uncertainty interval, and unseen-prime control.
8. Charge complete costs and preserve the comparison boundary. Include
   field construction, maximal-order computation, prime-ideal factoring,
   descent, generator search and saturation, height evaluation, point
   enumeration, reduction, deduplication, and target verification. Compare
   those costs with the same-field rho baseline. A negative result for this
   field family is not an obstruction for all number-field transfers.

## Readiness and disposition

The proposal is a useful adjacent control to the existing bounded-box lift
experiment, but its stated degree-one map is not automatic and its rank and
coverage metrics currently mix certified facts with censored or enumerated
subsets. The matched random-field design and full resource accounting are
also incomplete.

Disposition: **retain proposed as a conditional SNFS-field lift control; do
not approve or dispatch as filed.** Repair the field/prime certificates,
curve reduction map, rank intervals, height semantics, matched controls,
coverage metrics, scale model, and complete cost accounting. Recheck runnable
state, dependencies, and approval capacity after a complete contract exists.
