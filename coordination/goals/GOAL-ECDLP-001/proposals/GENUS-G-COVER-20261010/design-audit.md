# Genus-g cover cost-floor design audit

## Audit basis

- Idea: `IDEA-20261009-275a14`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `H-ECDLP-bd1572`, `KR-IC-a4dd54`, `KR-IC-5ea2f8`,
  `KN-LIT-007`, `KN-LIT-068`, and `KN-LIT-92caf4`.

## Scientific boundary

The proposal is a useful control question: a cover and its Jacobian are built
over the same prime field, so any claimed benefit must be distinguished from
the base-field shrink that powers genuine descent attacks. The current text,
however, conflates a complexity result for a full Jacobian, recovery of a
specified elliptic factor, and the measured wall-clock behavior of a finite
implementation. The E-part projection and its cost are load-bearing; a
generic relation computation on `Jac(C)` does not automatically solve a
discrete logarithm in `E(F_p)`.

## Load-bearing repairs

1. Fix the geometric input and maps. For every cell, publish equations for
   `C`, the cover map, the Jacobian-to-`E` projection or correspondence, the
   isogeny kernel, and the conditions for good reduction. For genus two,
   gluing two-torsion must be certified and the resulting factors identified;
   for genus three, specify the actual decomposition rather than assuming a
   genus-based E-part.
2. Define the target problem in the Jacobian. State whether the input is a
   point in `E(F_p)`, a point in an explicitly embedded elliptic factor of
   `Jac(C)(F_p)`, or a divisor class with a known projection. Include the
   embedding, projection, kernel, cofactor, and exact conversion cost. A
   relation matrix for the full Jacobian is not evidence of E-part recovery
   unless the target map is exercised and verified.
3. Separate same-field controls from descent controls. The comparison must
   hold curve family, base field size, subgroup order, representation, and
   security target fixed. The descent-direction control must explicitly use
   `E/F_{q^g}` and document the restriction of scalars or descent map. A
   successful control validates the harness but does not transfer its cost
   exponent to the same-field cover.
4. Define the algorithmic cost model. Count factor-base construction,
   smoothness testing, relation collection, large-prime handling, sparse
   linear algebra, Jacobian arithmetic, projection to `E`, cofactor clearing,
   and target verification. Report wall time only as an observation; fit
   operation counts or calibrated primitive costs with memory and failure
   rates. The claimed exponent must not be inferred from five noisy sizes
   without a fit range, uncertainty interval, and predeclared model.
5. Make the rho baseline matched. Use the same group order, target subgroup,
   coordinate model, arithmetic backend, parallelism, and success criterion.
   Record rho calibration separately from cover setup and relation costs. A
   cover can lose even when its asymptotic relation stage looks favorable if
   the projection or matrix stage dominates.
6. State the theorem scope precisely. The expression `p^(2-2/g)` depends on
   the curve family, relation model, smoothness assumptions, and the meaning
   of `p`; it is not a universal lower bound for every algorithm on every
   cover. Label theorem-derived expectations, implementation measurements,
   and extrapolations separately, and do not turn a finite exponent fit into
   a proof of global nonexistence of a crossover.
7. Control factor-base and relation quality. Predeclare factor-base size,
   divisor degree/weight, smoothness bound, large-prime policy, relation
   rank, duplicate rate, and matrix dimensions. Require independent checks
   that every relation maps to zero and that the E-part target is represented
   with the claimed probability. “Restricted to the E-part” needs an
   executable, certificate-producing definition.
8. Keep the conclusion finite and comparative. The strongest admissible
   outcome is a measured cost comparison for the specified cover family,
   subgroup, implementation, and sizes, or an infrastructure failure. It
   cannot establish an asymptotic ECDLP lower bound, rule out all same-field
   correspondences, or show that a different representation has no benefit.

## Readiness and disposition

The proposal has a clear negative-control purpose and an appropriate
descent-direction comparison, but it lacks the explicit E-part maps, target
conversion, relation certificates, and complete cost decomposition needed to
make the central measurement interpretable. Its theorem-closed label does not
remove those implementation obligations.

Disposition: **retain proposed as a conditional same-field cover control; do
not approve or dispatch as filed.** Repair the cover/Jacobian certificates,
target embedding and projection, descent comparison, relation-quality gates,
matched rho baseline, and finite exponent model. Recheck runnable state,
dependencies, and approval capacity after a complete contract exists.
