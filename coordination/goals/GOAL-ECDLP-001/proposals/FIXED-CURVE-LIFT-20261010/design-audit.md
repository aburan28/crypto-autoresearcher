# Fixed-curve Q-lift-family design audit

## Audit basis

- Idea: `IDEA-20261009-29706a`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `H-ECDLP-bd1572`, `KR-IC-cd159a`, `KN-FIND-6b3e17`,
  `KN-FIND-e1b836`, and the rank-campaign certificates.

## Scientific boundary

The family
`y^2 = x^3 + (a + p s)x + (b + p t)` is a sensible way to generate
characteristic-zero curves whose reductions agree with a fixed curve over
`F_p`. A finite rank/height/coverage survey could document how often this
particular search family produces useful lifts. It does not, as currently
written, establish a universal rank ceiling, a proved height lower bound, or
an obstruction for all characteristic-zero lifts. The two-parameter sampling
law, specialization behavior, and union-of-reductions observable must be
made explicit before the measurements can support the intended comparison.

## Load-bearing repairs

1. Certify every lift and its reduction. Record integral coefficients,
   minimal model, discriminant, conductor, good-reduction status at `p`, and
   the exact reduction map. Exclude singular curves and account for minimal
   model changes. Confirm that all selected lifts reduce to the same curve
   and that the target subgroup is the same after reduction.
2. Separate the one-parameter theorem from the two-parameter sample. Fixing
   `t` gives a surface over `Q(s)`, while the experiment samples points in an
   `(s,t)` box. A generic rank statement over `Q(s)` does not bound the rank
   of every specialization, and a rational-surface geometric rank bound does
   not imply the proposed mean or maximum rank histogram. State exactly what
   theorem is used and treat specialization outliers as valid observations.
3. Replace the height conjecture with a measured quantity. Lang-type lower
   bounds are conditional and depend on the model, discriminant, local terms,
   and the constants in the chosen family. For each certified generator,
   report the canonical height, height-pairing matrix, saturation status,
   torsion, and whether the rank is proved or only bounded below. A loose
   two-descent or analytic-rank result must not be treated as a complete
   generator inventory.
4. Define the sampling and comparison distributions. Predeclare whether
   `(s,t)` is uniform over the integer box, filtered by minimality, prime
   conductor, analytic-rank availability, or successful descent. Match the
   random-curve controls on `p`, conductor band, discriminant scale, model
   minimality, torsion, and rank-certification method. Report selection and
   failure rates rather than dropping hard cells.
5. Make rank inference reproducible. Give exact descent bounds, analytic-rank
   precision and functional-equation checks, generator search limits,
   saturation tests, and the treatment of unresolved Tate--Shafarevich
   factors. A histogram mixing lower bounds, exact ranks, and censored cells
   cannot support mean or maximum thresholds without interval-valued analysis.
6. Define the coverage union. State which rational points are enumerated on
   each lift, the height normalization and cutoff, whether signs and torsion
   translates are included, and how reduction images are deduplicated. Report
   per-lift image size, union image size, subgroup order, target-hit rate, and
   exact decomposition certificates. The union over 10,000 lifts is a sample
   statistic, not coverage of all lifts.
7. Match the scale extrapolation. The proposed `p` values and `20 log p`
   cutoff need a declared logarithm/base convention, fit range, uncertainty
   propagation, and an unseen-prime or unseen-target panel. Two primes cannot
   justify a stable constant across 20- and 30-bit scales, much less a
   conclusion at cryptographic sizes, without a stated extrapolation model.
8. Charge search and certification costs. Include model reduction, conductor
   computation, descent, analytic evaluation, generator search and
   saturation, height computation, point enumeration, reduction, deduplication,
   and target checking. Compare the complete lift-search cost with the
   matched rho baseline. A low coverage fraction after an expensive lift
   search is an obstruction for this pipeline, not an end-to-end complexity
   result for every lift strategy.

## Readiness and disposition

The proposal has a well-defined finite family and a potentially reusable
coverage data set, but the current contract overstates what the rational
surface observation and height heuristic imply. Rank ascertainment, sampling
selection, reduction-image semantics, and full search costs are not yet bound
to the proposed thresholds.

Disposition: **retain proposed as a conditional fixed-curve lift-family
measurement; do not approve or dispatch as filed.** Repair the per-lift
certificates, specialization scope, rank-censoring policy, matched control,
coverage definition, scale extrapolation, and complete cost accounting.
Recheck runnable state, dependencies, and approval capacity after a complete
contract exists.
