# ECDLP-IDEA-366 — Razborov flag-algebra source density

## Status and claim labels

- Class: `measurement`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_flag_algebra_returns_asymptotic_aggregate_not_exact_source`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an extremal density certificate or SDP optimum is not an ECDLP break.

## Falsifiable hypothesis

Finite labelled flags of the elliptic relation hypergraph determine a bounded flag-algebra quotient whose positive homomorphisms yield an exact restricted-existence decision and source atom below the P1553 gates.

## Mechanism-new operation

The screened operation is **map local relation motifs into a flag algebra, multiply labelled flags, impose positivity through semidefinite constraints, and round an extremal homomorphism to one exact relation edge**. It is distinct only if flag densities are endpoint-derived without enumerating edges, asymptotic identities are zero-safe for rare fibres, and rounding returns labels under arbitrary restrictions.

## Assumptions

1. Bounded-size flag densities can be computed from public endpoints below the setup/query gates.
2. The flag quotient separates empty from nonempty restricted target fibres, including singleton fibres.
3. Positivity/SDP solutions have a public exact rounding or self-reduction to signed labelled points.
4. Finite-size errors, characteristic effects, and target updates remain uniform and fully charged.
5. Density construction, SDP time/state, precision, rounding, output, rank, logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_relation_hypergraph | endpoint_local_flag_densities | Razborov_flag_algebra_product | SDP_positive_homomorphism | exact_restricted_edge_rounding | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H675`; local motifs must construct the missing source-resolving interface.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`; fibre generation and target batching remain dominant.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; exact flag counts from an edge list already consume source incidence.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`; exact source statistics from pair generation restore cubic work.
5. `inputs/ledger_inventory.json` — imported `ECFG-P1435-EXACT-GENERATOR-AND-BATCH-CONTROL`; supplied relation streams are controls.

## Closest primary literature

- Razborov, [Flag Algebras](https://doi.org/10.2178/jsl/1203350785), develops asymptotic homomorphism-density calculus for supplied finite relational structures.
- Razborov's [primary manuscript page](https://homepage.mi-ras.ru/~razborov/flag/) gives the formalism and extremal applications, not exact rare-edge recovery from endpoints.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the relation predicate but not cheap flag densities or a source rounding map.

No checked source supplies the complete ECDLP path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, flag types, labelling, density estimator, SDP basis, restrictions, masks, and verifier.
2. Construct target-independent flag data from endpoints without relation-edge enumeration.
3. On known-log targets, solve exact restricted nonemptiness/rounding and replay returned tuples.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Reuse identical flag data and target updates for fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge densities, SDP, precision, rounding, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Flag algebras constrain limiting aggregate densities of represented structures. Rare target fibres may differ by one edge while sharing every bounded flag statistic asymptotically; SDP positivity does not return labels. Computing exact densities already enumerates relation motifs, and finite rounding restores source search. This merges with aggregate/SDP lanes IDEAs 104, 200, 303, 328, 335, and 348.

## Proof track

Prove a bounded flag basis exactly separates every restricted fibre and give an endpoint-only exact rounding algorithm with complete exponents at most `0.45`.

## Disproof track

Construct empty/nonempty fibres with identical permitted flag data, show rounding requires an edge oracle, or charge density/SDP work above the gates.

## Positive and negative controls

- Positive: supplied dense graphs with extremal configurations certified by a small flag SDP and known edges.
- Negative: relation hypergraphs differing by one hidden edge, source permutations, finite-size pseudorandom controls, and blind targets.
- Baselines: IDEAs 104/200/303/328/335/348, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only exact flag data, zero-error restricted decisions/rounding, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on indistinguishable empty/nonempty fibres, source-edge input, approximate-only density, one missed stratum, `B^3` motif work, or either exponent at least `0.50`.
- An extremal SDP certificate on a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-366/flag_separation_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-366/finite_flag_collision_cases.json`
- `ideas/artifacts/ECDLP-IDEA-366/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-366/cost_analysis.md`

## Interpretation boundary

This rejects the screened exact-source use of flag algebras, not their extremal-combinatorics results. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. An SDP bound is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-366/flag_separation_obligations.md` and search for empty/nonempty restricted fibres sharing every subgate flag statistic.
