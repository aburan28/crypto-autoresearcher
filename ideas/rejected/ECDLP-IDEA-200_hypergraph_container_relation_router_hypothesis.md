# ECDLP-IDEA-200 — Hypergraph-container relation router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_container_requires_relation_hypergraph_or_exact_edge_oracle`
- Cohort: `20260718-d`
- Evidence scale: literature and input-oracle audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective finite checks are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a container, relation count, or valid source tuple is not an ECDLP break.

## Falsifiable hypothesis

The five-source relation hypergraph on a factor base admits a target-independent family of few small containers computable from local co-degree queries. Intersecting those containers with known-log and masked target fibers then locates and exactly unpacks enough independent relations with complete time and memory below rho and BSGS.

## Mechanism-new operation

The proposed operation is **co-degree-driven containerization followed by endpoint-conditioned exact hyperedge unranking**. It attempts to replace the explicit `B^5` source hypergraph by a short structural cover rather than by a solver or dense resultant. The audit rejects the current version because hypergraph-container theorems consume an edge/co-degree oracle and return approximate vertex-set supersets; neither operation constructs a rare target hyperedge or its labelled sources.

## Assumptions

1. Public `E/F_p`, prime-order `G=<P>` of order `N`, factor base `F` of size `B=N^beta`, and target `Q=[x]P` are frozen.
2. The relation hypergraph and every co-degree query are constructed without enumerating source tuples or partial-sum edges.
3. The number and total encoded size of containers are at most `B^2.25`.
4. Endpoint intersection returns every exact signed source, including repeats, vertical pairs, infinity, and multiplicity.
5. Container construction, oracle calls, failed targets, output, rank, factor logs, blind descent, verification, and bit memory are charged.

## Semantic fingerprint

`five_source_relation_hypergraph | local_codegree_oracle | sparse_container_cover | endpoint_conditioned_exact_edge_unranking | blind_masked_descent`

The fingerprint fails if the hypergraph or its co-degrees are materialized, if containers only count independent sets, or if exact edges are selected post hoc.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-RT-1476`, the required implicit membership/query rectangle.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-edge charge.
4. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-state control.
5. `inputs/ledger_inventory.json` — imported `ECFG-H642`, the structured-coordinate support-router frontier.

## Closest primary literature

- Saxton and Thomason, [Hypergraph containers](https://arxiv.org/abs/1204.6595), covers independent sets of a supplied low-co-degree hypergraph rather than rare target-edge location.
- Balogh, Morris, and Samotij, [Independent sets in hypergraphs](https://arxiv.org/abs/1204.6530), likewise assumes access to the hypergraph and produces approximate containers.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies elliptic relation equations but no co-degree or exact-edge oracle.

No checked primary source supplies the proposed endpoint router; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the hypergraph definition, co-degree oracle, container parameters, endpoint predicate, masks, and verifier.
2. Construct the oracle and container family without source or transition enumeration.
3. Intersect known-log endpoints with the containers and unrank every exact signed hyperedge.
4. Independently verify relations and preserve false positives, multiplicities, collisions, infinity, and empty endpoints.
5. Collect at least `B+sigma` independent rows, solve factor-base logs, and verify them.
6. Apply the identical frozen router to fresh masks `Q+[r]P`.
7. Substitute verified factor logs, subtract `r`, retain ambiguity, and accept only `[x]P=Q`.
8. Serialize setup, oracle traffic, container size, queries, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let setup be `N^a,N^a_m`; reciprocal relation and target densities be `N^delta,N^delta_t`; one container query and exact lift be `N^q,N^q_m`; independently ranked rows per query be `N^r`; output and ambiguity exponents be `o,u`; and factor-log linear algebra be `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Promotion would require both exponents at most `0.45`; a small number of containers without charged oracle and exact-edge costs is non-promoting.

## Likely fatal obstruction

Container theorems compress families of independent or sparse vertex sets after the hypergraph and its co-degrees are available. The ECDLP task is instead to locate rare endpoint-labelled hyperedges. Computing the required co-degrees exposes the same partial-sum/source deck, while refining an approximate container to an exact relation requires `B^5` edge search or the missing completion oracle.

## Proof track

Give a sub-`B^2.25` target-independent co-degree circuit, prove that its containers isolate exact endpoint hyperedges with all-strata source replay, and derive `lambda,mu<=0.45` through factor logs and blind descent.

## Disproof track

Reduce any co-degree query to explicit source edges, exhibit a container with exponentially many endpoint candidates, prove exact refinement costs `Omega(B^3)` state or `Omega(B^5)` work, or derive `max(lambda,mu)>=0.50`.

## Positive and negative controls

- Positive control: supplied sparse toy hypergraphs with enumerated co-degrees and withheld edges.
- Negative control: approximate independent-set containers without endpoint labels.
- Negative control: explicit relation hypergraphs, source-edge tables, post-hoc selectors, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires container construction and total size at most `B^2.25`, one-row endpoint query at most `B^1.25`, 100% exact source and multiplicity recall, zero false tuples, no explicit source-edge oracle, and `lambda,mu<=0.45`. Materialized co-degrees, `Omega(B^3)` retained state, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective oracle theorem: `ideas/artifacts/ECDLP-IDEA-200/codegree_oracle_theorem.md`
- Prospective exact-edge specification: `ideas/artifacts/ECDLP-IDEA-200/container_edge_unranking_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-200/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified algorithm analysis. Finite evidence would be toy and all scaling heuristic and model-bound. A container, count, valid relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-200/codegree_oracle_theorem.md` giving a source-free sub-`B^2.25` co-degree circuit with exact endpoint-edge unranking or proving that the required oracle materializes `Omega(B^3)` source state.
