# ECDLP-IDEA-309 — Cartier test-ideal source stratifier

## Status and claim labels

- Class: `positive_characteristic_algebraic_geometry`
- Risk band: `conservative`
- Top lane: `conservative`
- State: `merged_rejected_test_ideal_is_unit_on_generic_reduced_source_locus`
- Cohort: `20260718-m`
- Evidence scale: exhaustive semantic and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run `review_required` preflight draft
- Scale labels: every prospective finite check is `toy`; all extrapolations are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct Cartier-module computation, nontrivial singular stratum, valid relation, or toy point split is not an ECDLP break.

## Falsifiable hypothesis

The Cartier algebra and its test ideals on a summation-polynomial source fiber form a compact, endpoint-computable Frobenius-stable filtration whose strata isolate exact factor tuples, yielding source-complete relations and blind masked-target descent below rho and BSGS.

## Mechanism-new operation

The screened operation is **construct the source fiber's Cartier algebra, iterate Frobenius-trace-compatible ideals to a test ideal, and use the resulting F-pure or test-ideal strata as a canonical router from an endpoint component to exact signed factor points**. This differs from a generic factorization or dense resultant because the proposed separator is intrinsic positive-characteristic singularity data. For the full Cartier algebra on an unadorned regular finite-etale source locus, the standard test ideal is the unit ideal and the Cartier structure is uniform; this statement is not asserted for every chosen Cartier subalgebra or Cartier pair. The intrinsic filtration can mark special singular or nonreduced loci without naming generic rational points. Point separation then requires primitive idempotents or component factorization, restoring explicit source materialization. The proposal merges with IDEAs 097, 159, 216, 228, and 250.

## Assumptions

1. A compact target-uniform Cartier algebra and test-ideal chain are computable from the endpoint fiber without factoring its source algebra or listing its rational points.
2. The filtration separates every generic reduced factor tuple as well as collision, signed, inseparable, and nonreduced strata.
3. Each surviving stratum has a canonical biconditional lift to exact signed factor points rather than only a singular-locus or multiplicity certificate.
4. Cartier maps, Frobenius powers, ideal arithmetic, field extensions, point output, relation rank, factor logs, descent, verification, time, and peak memory are charged.

## Semantic fingerprint

`summation_source_fiber | Cartier_p_minus_e_linear_algebra | test_ideal_F_pure_stratification | exact_factor_point_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator and transposed join.
2. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate barrier for rational maps and recursive source expansion.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1449`, the negative coordinate-expansion matrix preflight.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1426-MATERIALIZED-PRODUCT-NO-PROMOTION`, the exact source-recoverable product whose materialization fails promotion.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-incidence boundary.

## Closest primary literature

- Blickle, [Test ideals via algebras of p^-e-linear maps](https://arxiv.org/abs/0912.2255), develops test ideals from Cartier-style operator algebras for supplied positive-characteristic schemes; it does not claim generic closed-point separation.
- Schwede, [Centers of F-purity](https://arxiv.org/abs/0807.1654), studies Frobenius-compatible centers and F-pure structure, which identify special subvarieties rather than a canonical label for each generic point.
- Blickle and Bockle, [Cartier modules: finiteness results](https://arxiv.org/abs/0909.2531), proves structural finiteness for Cartier modules, not a source-free inverse for finite-field endpoint fibers.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the endpoint fiber without a Cartier/test-ideal factor decoder.

No checked source provides the hypothesized generic point-separating filtration, exact all-strata factor inverse, blind descent, or complete sub-rho cost path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, source-fiber presentation, Cartier generators, test-ideal iteration, stratum-to-point inverse, masks, and independent verifier.
2. For random known-log endpoints, construct the Cartier/test-ideal filtration without factoring the source algebra, enumerating rational points, or supplying source-labelled components.
3. Traverse every Frobenius-stable stratum, return all exact signed factor tuples, and independently verify each endpoint relation.
4. Collect independent verified rows, solve the complete factor-log system, and verify every recovered factor logarithm.
5. Apply the identical Cartier algebra, iteration, and inverse to fresh masked targets `Q+[t]P` without target-trained strata, selectors, or source advice.
6. Substitute factor logs, remove masks, retain all component, field-extension, nilpotent, and sign ambiguity, and return every scalar candidate.
7. Accept only exact `[x]P=Q`, charging Frobenius and ideal arithmetic, component handling, point outputs, failures, rows, logs, descent, verification, time, and peak memory.

## Full rho/BSGS cost model

With setup `N^a,N^a_m`, factor base `N^beta`, reciprocal relation and target densities `N^delta,N^delta_t`, one Cartier/test-ideal/point-inverse attempt `N^q,N^q_m`, independent-rank gain `N^r`, output `N^o`, target ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

`q` includes Cartier-algebra construction, Frobenius and ideal operations, every component lift, exact inverse, and independent verification; `o` includes all strata, components, extension points, and tuples returned. Rho has expected time exponent `1/2` and negligible memory; BSGS has time and memory exponents `1/2`.

## Likely fatal obstruction

Test ideals and F-pure centers detect singularity and Frobenius-compatible substructure, not arbitrary labels among generic smooth points. For the full Cartier algebra on the unadorned regular finite-etale source algebra, the standard test ideal is the unit ideal and the local Cartier behavior is uniform, so all valid factor tuples occupy the same intrinsic stratum. This does not close arbitrary chosen Cartier subalgebras or Cartier pairs. Separating generic points in the frozen arm requires decomposing the algebra into primitive idempotents, factoring its components, or enumerating its rational points—the source-complete operation whose charged size and output the proposal sought to avoid.

## Proof track

Construct a compact endpoint-uniform Cartier algebra and prove its test-ideal filtration separates all generic reduced points and exceptional strata biconditionally into exact signed factor tuples, then prove sufficient independent rows, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Prove the full-Cartier-algebra test ideal is the unit ideal on the preregistered unadorned regular finite-etale source locus and that its intrinsic strata are point-indistinguishable there, or show the frozen point-separating refinements compute primitive idempotents/components with exponent at least `0.50`.

## Positive and negative controls

- Positive: a supplied nonreduced or singular finite scheme with known nontrivial test ideal must recover the preregistered Frobenius-compatible special stratum.
- Negative: a product of isomorphic finite separable fields with permuted primitive idempotents must remain point-indistinguishable unless the idempotents are explicitly supplied or computed.
- Baselines: direct finite-algebra factorization, primitive-idempotent decomposition, IDEAs 097/159/216/228/250, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with an independent generic-plus-exceptional source biconditional, 1,000 verified rows and 100 blind descents per large size, and both complete exponents at most `0.45`.
- Falsify if the full-Cartier-algebra test ideal is unit on the unadorned regular finite-etale locus, point separation needs primitive idempotents or component factoring, or charged ideal/state/output reaches exponent `0.50`.
- Exponents in `(0.45,0.50)` are inconclusive and non-promoting.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-309/cartier_test_ideal_stratification_theorem.md`
- `ideas/artifacts/ECDLP-IDEA-309/fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-309/independent_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-309/cost_analysis.md`

## Interpretation boundary

This is a scoped semantic rejection of generic source-point recovery by the stated Cartier/test-ideal stratifier, not a universal impossibility theorem for F-singularity methods. The conservative lane retains a retired zero-run `review_required` preflight draft solely to preserve the theorem check; no experiment may run. Correct singular-stratum detection, relation validity, or toy separation is not scalar recovery or a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-309/cartier_test_ideal_stratification_theorem.md` proving the unit-ideal/generic-point-indistinguishability boundary or a compact counterexample before this retired draft may be approved or any experiment may run.
