# Q-lift rank-coverage design audit

## Audit basis

- Idea: `IDEA-20261009-0bb2cf`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `H-ECDLP-bd1572`, `KR-IC-cd159a`, `KN-TECH-060`,
  `KN-FIND-fd382f`, and the rank-campaign point and independence certificates.

## Scientific boundary

The proposal can measure how a selected Mordell--Weil lattice and a specified
reduction map constrain a bounded-height factor-base construction. That is a
useful quantitative obstruction study, but the current record combines three
different statements: a lattice-point counting approximation, coverage of a
finite reduction group, and the rank needed to reach a target coverage level.
Those statements require separate observables and controls. A fitted count on
the rational lattice does not by itself certify useful independent relations,
surjective reduction, or an index-calculus complexity bound.

## Load-bearing repairs

1. Fix the arithmetic setting per curve. Record the exact base field, curve
   model, torsion subgroup, certified independent generators, their full
   height-pairing Gram matrix, and whether the rank is a lower bound or a
   proved rank. For generators over a multiquadratic field, state the field,
   degree, Galois action, and the degree-one prime used for reduction; do not
   mix those cells with curves over `Q` in one rank comparison.
2. Define `N(H)` unambiguously. State the height normalization, whether the
   count is modulo torsion, sign, and Galois symmetries, how boundary points
   are handled, and whether the enumeration is over the complete Mordell--Weil
   group or only the certified sublattice. A lower-bound generator lattice
   cannot be presented as a count for the full group without an explicit
   qualification.
3. Separate asymptotic fit from finite geometry. The expression
   `V_r H^(r/2) / sqrt(Reg)` is an asymptotic lattice-volume term; its error
   depends on successive minima and boundary geometry. Fit each curve over a
   preregistered range with residuals and confidence intervals, report the
   shortest-vector and anisotropy diagnostics, and compare with determinant-
   and minimum-vector-matched random lattices. The `2x` threshold needs a
   declared loss function and treatment of zero or small counts.
4. Correct the sumset bound. If every factor-base element has height at most
   `H_F`, an `m`-term sum has height at most `m^2 H_F`, so the number of
   distinct sums is at most the number of eligible lattice points at that
   height. This is only an upper bound, not an estimate of coverage: exact
   `m`-sum reachability, signs, torsion translates, repeated summands, and
   reduction collisions must be measured separately. Record both the raw
   rational sumset and its image in the selected finite subgroup.
5. Specify the reduction and target space. Certify good reduction and the
   reduction homomorphism, compute the order of the image of the certified
   subgroup, and sample targets from that image as well as from the intended
   ECDLP subgroup. Coverage of all of `E(F_p)` is not the right denominator
   when the reduction image or target subgroup is smaller. Include an
   independent target panel and exact membership/decomposition certificates.
6. Make the coverage comparison dimensionally complete. The record uses
   `m^r |F| / p` as a heuristic, but the relevant quantity depends on the
   number of ordered or unordered sums, collisions, torsion, the subgroup
   order, and the actual `|F|`. Report the observed image cardinality, unique
   sumset cardinality, target-hit rate, and collision rate, with a matched
   random-lattice and random-subset control at the same rank, determinant,
   factor-base size, and finite-group order.
7. Define the rank extrapolation before measuring it. State the chosen `m`,
   height budget, regulator/shortest-vector model, and finite-group size for
   the 128- and 256-bit projections. Propagated uncertainty from the fit and
   from the regulator distribution must produce an interval for required rank;
   a single threshold such as 60 or 100 is not supported by finite rank-5--31
   cells without an explicit extrapolation model and sensitivity analysis.
8. Charge all construction and target costs. Include generator certification,
   height-pairing computation, enumeration, reduction, deduplication,
   sumset construction, membership testing, and target verification. Compare
   those costs with a matched Pollard-rho baseline and state memory as well as
   time. A coverage obstruction is not an end-to-end ECDLP speedup or a proof
   that every lift strategy fails.

## Readiness and disposition

The record has a plausible finite measurement objective and useful reuse of
rank-campaign certificates, but its current contract does not distinguish the
certified sublattice from the full Mordell--Weil group, does not bind the
reduction image and target subgroup, and treats a volume heuristic as a
coverage prediction. The 128-/256-bit rank thresholds also require a declared
extrapolation and uncertainty model.

Disposition: **retain proposed as a conditional Q-lift obstruction
measurement; do not approve or dispatch as filed.** Repair the arithmetic
cell definitions, exact height-count semantics, sumset and reduction-image
metrics, matched controls, extrapolation interval, and full cost accounting.
Recheck runnable state, dependencies, and approval capacity after a complete
contract exists.
