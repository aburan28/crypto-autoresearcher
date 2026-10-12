# Required-section-height design audit

## Audit basis

- Idea: `IDEA-20261009-fb9bae`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `IDEA-20261009-0bb2cf`, `KN-FIND-91f871`, `KN-TECH-060`,
  and the SNFS-E1/E3 lift contracts.

## Scientific boundary

The proposed table could provide a useful parameter estimate for a specified
Mordell--Weil lattice and a specified section construction. Its current claim
connects three separate quantities—lattice-point count, height needed for
finite-group coverage, and section degree/unknown count—without defining the
map between them. Synthetic rank-50/100/300 lattices are valuable controls,
but they are not evidence about Mordell--Weil lattices unless the extrapolation
is explicitly labeled and stress-tested.

## Load-bearing repairs

1. Fix the height geometry. State whether `H` is canonical height, squared
   Euclidean norm, section degree, or a multiple of one of these; give the
   normalization of the regulator/determinant and the exact `lambda_1`. The
   threshold `3 lambda_1^2` is not a general guarantee that boundary effects
   are within 2x, especially for anisotropic lattices.
2. Define the point-count observable. Specify quotienting by torsion and sign,
   boundary inclusion, saturation, and whether `N(H)` counts the full
   Mordell--Weil group or only a certified sublattice. Report successive
   minima, anisotropy, residuals, and uncertainty per E1 lattice; use a
   determinant- and minima-matched random-lattice control.
3. Derive the coverage threshold with the correct target space. State the
   reduction prime, subgroup order, factor-base definition, allowed sum arity,
   and whether coverage means distinct reductions, reachable sums, relation
   rank, or target decomposition. Requiring `N(H) >= p` is not generally the
   right condition when the reduction image is a proper subgroup or when the
   construction uses sums of a factor base.
4. Define section degree and unknown count. Give the exact function-field
   construction mapping height/section degree to polynomial degree and number
   of equations/unknowns. The record’s `H about 650` does not by itself imply
   a section degree above 100 or a system with about 1,000 unknowns; those
   conversions need formulas, constants, and a costed implementation.
5. Separate measured and synthetic cells. E1 curves can calibrate the finite
   range, while rank-50/100/300 lattices test a chosen geometric model. Match
   determinant, shortest vector, Gram-spectrum shape, and arithmetic precision;
   report sensitivity when each is varied. Do not infer a Mordell--Weil law
   from synthetic lattices merely because their determinant was matched.
6. Make the 64/128/256-bit extrapolation reproducible. State logarithm base,
   regulator model, rank grid, height cutoff, finite-group order, rounding,
   and propagated uncertainty. Include an unseen-rank/parameter panel and
   sensitivity to the unknown multiplicative constant in the Gaussian model.
   A threshold above 100 for `r <= 100` is a model output, not a theorem.
7. Charge enumeration and downstream costs. Include Gram-matrix construction,
   exact enumeration, duplicate removal, reduction, section generation,
   relation formation, sparse linear algebra, target checking, memory, and
   failure rates. Compare the complete path with a matched rho baseline;
   parameter size alone does not establish an ECDLP obstruction.
8. Preserve the interpretation boundary. A 2x fit and a large required
   section degree would be finite evidence for the measured lattice model.
   It would not prove that all high-rank lifts, non-lattice factor bases, or
   other correspondences have the same cost.

## Readiness and disposition

The proposal is a useful parameter-table companion to the Q-lift rank audit,
but its central height-to-section-degree conversion and coverage denominator
are not specified. The synthetic high-rank extension is also a model check,
not a certified arithmetic result.

Disposition: **retain proposed as a conditional section-height measurement;
do not approve or dispatch as filed.** Repair the height/count definitions,
target subgroup and sumset model, section-degree map, synthetic-lattice
matching, extrapolation intervals, and full cost accounting. Recheck runnable
state, dependencies, and approval capacity after a complete contract exists.
