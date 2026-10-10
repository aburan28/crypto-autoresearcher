# Fiber-product varieties for relation generation

Status: proposed research experiment; no speedup or novelty claim.

## Research hypothesis
Construct E1 x_E0 E2 and analyze components, genus, parametrization and equations for potential factor-base relations.

## Experimental protocol
Compare dimensions, verified relation counts and total solving cost against direct isogeny and standard index-calculus controls.

## Required implementation
1. Review prior art, theorem assumptions, and negative results; record verified DOI/arXiv/ePrint references.
2. Construct Sage reference instances over small ordinary prime/binary fields with certified maps, kernels, conductors and subgroup orders.
3. Implement baseline and treatment with deterministic seeds, fixed budgets and identical hardware/solver settings.
4. Record setup, map construction, fiber work, failed targets, solver timeouts, duplicates, rank, verified independent relations, linear algebra, and final verification.
5. Extend to binary m=31,51,53,83 when valid, prime fields and extension fields; include same-trace paired controls.
6. Compare total cost per verified independent relation and end-to-end solve time with confidence intervals, and publish negative results.

## Correctness constraints
For separable degree-ell isogeny geometric fibers are kernel cosets; do not confuse geometric with rational points. For subgroup prime order r coprime to ell, isogenies preserve scalar information and do not reduce the search space. Include transfer cost and alternative isogeny paths. Do not mistake solver-coordinate effects for intrinsic ECDLP hardness.

## Deliverables
- Literature/evidence note and novelty matrix
- Reproducible Sage generator and small-field unit tests
- Paired F4/F5/SAT benchmarks where applicable
- Structured metrics, plots, failures, and falsification report

## Acceptance criteria
Certified mathematical objects; exact relation verification; matched controls; accounting for unsuccessful attempts; statistically meaningful results; no unsupported security claims.

Related umbrella research: #2047.
