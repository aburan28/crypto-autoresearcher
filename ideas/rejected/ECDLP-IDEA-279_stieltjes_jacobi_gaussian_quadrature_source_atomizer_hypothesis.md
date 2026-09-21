# ECDLP-IDEA-279 — Stieltjes-Jacobi Gaussian-quadrature source atomizer

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_quadrature_atomization_requires_source_moments_and_loses_tuple_pairing`
- Cohort: `20260718-k`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: `retired_zero_run_review_required`
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a Jacobi matrix, quadrature rule, recovered atom, valid relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Endpoint-computable moments of an ECDLP source fiber determine a sparse discrete measure whose atoms encode the exact factor points.  A finite-field Stieltjes procedure followed by the Golub-Welsch Jacobi-matrix eigensolve would atomize that measure and return complete factor tuples for relation collection and fresh-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **map a source fiber to a moment functional, recover its three-term recurrence and Jacobi matrix, and use Gaussian-quadrature nodes and weights as exact source atoms**.  This is a moment-to-support reconstruction algorithm rather than an explicit large-prime table, dense resultant, or generic solver substitution.  Classical Gaussian quadrature assumes enough moments of the unknown measure and returns nodes of the orthogonal polynomial; it does not manufacture source-sensitive moments from an endpoint.  Moments that identify `s` arbitrary atoms require order `s` information, while coordinate-wise atomization loses the pairing, signs, and multiplicities needed for elliptic-curve source tuples.  Thus the operation merges with quotient/moment-algebra and source-materialization negatives after moment generation, Jacobi state, atom output, and pairing are charged.

## Assumptions

1. Public source equations and an endpoint yield a deterministic finite-field moment functional without enumerating or labelling source tuples.
2. A nonsingular Stieltjes-Jacobi recurrence exists on every characteristic and degeneracy stratum relevant to the factor base.
3. Quadrature nodes and weights canonically pair into exact signed elliptic-curve factor tuples with sub-rho ambiguity.
4. Moment generation, Hankel arithmetic, recurrence coefficients, eigensolving, roots, weights, pairings, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`prime_field_ECDLP | endpoint_source_moments | Stieltjes_three_term_recurrence | Jacobi_Gaussian_quadrature_atoms | exact_factor_tuple_return`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `P1477`, the compact-invariant-to-exact-source return boundary.
3. `inputs/ledger_inventory.json` — imported `P1478`, the dense source state and output frontier.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, the compressed aggregate statistic without source output.
5. `inputs/ledger_inventory.json` — imported `ECFG-H643`, the moment/recurrence representation hypothesis and source-recovery boundary.

## Closest primary literature

- Golub and Welsch, [Calculation of Gauss quadrature rules](https://doi.org/10.2307/2004418), derives Gaussian-quadrature nodes and weights from the symmetric tridiagonal Jacobi matrix built from recurrence coefficients.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the finite-field source equations from which endpoint-only moments would have to be obtained.

No checked source derives compact source-faithful moments from a generic ECDLP endpoint or supplies an all-strata sub-rho atom-to-factor return; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the finite-field instance, source equations, moment basis and order, Stieltjes convention, Jacobi eigensolver, factor base, masks, and verifier.
2. Generate complete moment sequences for known-log relation endpoints and construct every required Hankel form and Jacobi matrix without source enumeration.
3. Recover all quadrature nodes and weights, resolve repeated or isotropic cases, pair the atoms, and map every accepted result to exact signed factor points.
4. Verify the resulting relations, collect independent rows, solve every factor log, and verify all recovered logs.
5. Apply the identical frozen moment and quadrature pipeline to fresh masked targets `Q+[t]P` without target-specific tuning or source advice.
6. Retain every admissible atom pairing, return a complete factor decomposition or scalar residue, remove the mask, and verify the reconstructed endpoint.
7. Accept only exact `[x]P=Q`, charging moments, Hankel/Jacobi state, roots and weights, pairing ambiguity, failed attempts, rows, factor logs, fresh-target descent, verification, and live memory.

## Full rho/BSGS cost model

Pollard rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.  Let setup time and memory be `N^a,N^a_m`, factor-base size be `N^beta`, reciprocal relation and target success densities be `N^delta,N^delta_t`, one moment/Stieltjes/quadrature/return attempt cost `N^q,N^q_m`, independent-rank gain be `N^r`, atom and pairing output be `N^o`, recurrence or pairing ambiguity be `N^u`, and factor-log completion be `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every moment, Hankel entry, recurrence coefficient, Jacobi entry, field extension, eigenvalue/root, quadrature weight, atom pairing, failed return, row, factor log, verifier step, and live byte is charged.

## Likely fatal obstruction

Gaussian quadrature reconstructs atoms only from a sufficiently informative supplied moment functional.  Generating source-faithful moments from an endpoint is already an aggregate source-enumeration problem: fewer moments collide, while enough moments make the Hankel/Jacobi dimension and output track the number of branches.  Moreover scalar or coordinate moments recover an unordered marginal support, not the correlated signed elliptic-curve tuple; restoring those correlations requires mixed moments whose count materializes the source algebra.  Finite-field isotropy, inseparability, and repeated nodes add failure strata but do not remove this information barrier.

## Proof track

Construct endpoint-only moments of exponent at most `0.45` that identify every source tuple, prove an all-strata finite-field Stieltjes-Jacobi atomizer and exact pairing/return, and certify both complete exponents at most `0.45`.

## Disproof track

Exhibit distinct source fibers with identical frozen moments, prove source-faithful moment order or atom/pairing output at least `N^0.50`, show mixed moments import source enumeration, find unavoidable singular finite-field strata, or derive either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied small discrete measure with distinct labelled atoms, exact moments through the identifying order, and a nonsingular Jacobi recurrence.
- Negative controls: truncated moment sequences with colliding supports, independently atomized coordinate marginals, repeated nodes, singular Hankel forms, random endpoint moments, explicit source tables, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires endpoint-only source-faithful moments and atomization of exponent at most `0.45`, exact all-strata atom pairing and factor return, full row rank and verified factor logs, blind fresh-target descent, and complete `lambda,mu<=0.45`.  Moment collisions, unpaired marginals, source-labelled moments, Hankel/atom/output/state at least `N^0.50`, or either exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-279/stieltjes_jacobi_atomizer_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-279/fixtures.json`
- Prospective independent verifier: `ideas/artifacts/ECDLP-IDEA-279/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-279/cost_analysis.md`

All four paths are prospective; no artifact root exists and no experiment ran.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative conservative algorithm proposal.  Every finite quadrature computation would be toy and projections heuristic and model-bound.  Correct moments, nodes, weights, a relation, or a recovered toy atom do not establish a generic-prime ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-279/stieltjes_jacobi_atomizer_theorem.md` proving compact endpoint-only moment identification and exact factor pairing or the moment-order/marginal-collision/source-state obstruction.
