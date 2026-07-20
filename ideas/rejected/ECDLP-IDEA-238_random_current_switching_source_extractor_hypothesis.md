# ECDLP-IDEA-238 — Random-current switching source extractor

## Status and claim labels

- Class: `statistical_representation`
- Risk band: `high_risk`
- Top lane: `-`
- State: `merged_rejected_current_graph_requires_source_vertices_and_switching_aggregates_paths`
- Cohort: `20260718-g`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a switching identity, connection event, or sampled current path is not an ECDLP break.

## Falsifiable hypothesis

Each signed elliptic factor-base endpoint admits a compact source-blind Ising random-current
encoding in which duplicating independent currents and applying the switching lemma turns an
endpoint correlation into canonical source-connecting paths.  Returning the path endpoints as exact
factor points would enable full relation collection and fresh masked-target descent below rho and
BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-to-random-current compilation, duplicated-current coupling,
switching-lemma source reassignment, and current-path-to-exact-point return**.  A supplied
point-labelled graph, generic graphical-model solver, Bethe loop expansion, path sampler without
exact coverage, high-temperature series, parameter change, or post-hoc endpoint selector is a
duplicate or control.

## Assumptions

1. `E/F_p`, prime-order `G=<P>` of size `N`, factor base `F` of size `B=N^beta`, signs, masks, current graph, couplings, and source set are target-independent.
2. The graph and integer-current ensemble have sub-rho represented size and can be compiled from an endpoint without a vertex, edge, coupling, or boundary source per point tuple.
3. Switching gives a canonical, exact, all-strata inverse to every signed elliptic source rather than only an aggregate correlation or connectivity event.
4. Partition-function normalization, exact current generation/counting, path ambiguity, source output, rank loss, factor logs, descent, verification, and peak memory are fully charged.

## Semantic fingerprint

`elliptic_endpoint_random_current_ensemble | duplicated_integer_currents | switching_lemma_source_reassignment | canonical_current_paths_to_exact_points | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the open endpoint source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the failed concrete-coordinate source predicate.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the failed arithmetic pair/four-sum source generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the measured source-ancestry edge boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-transition boundary.

## Closest primary literature

- Aizenman, [Geometric analysis of phi-four fields and Ising models](https://doi.org/10.1007/BF01205659), develops the random-current representation and switching method for supplied Ising graphs and correlations.
- Aizenman, Duminil-Copin, and Sidoravicius, [Random Currents and Continuity of Ising Model's Spontaneous Magnetization](https://arxiv.org/abs/1311.1937), uses switching identities to relate supplied current sources and connectivity events.

Neither source constructs an Ising/current graph from a generic elliptic endpoint, compresses its
source-labelled vertices, or recovers exact factor points from an aggregate switching identity.
Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,beta`, arity, signs, masks, current graph, couplings, boundary sources, duplicate-current law, switching/path rule, point inverse, and verifier.
2. Compile the endpoint graph and exact current ensemble without enumerating point sources or source-labelled incidence edges.
3. Evaluate or generate the required paired currents, apply switching, return every canonical source-connecting path and exact signed point tuple, and verify elliptic sums.
4. Collect independent relation rows, solve all factor logs, and independently verify rank and logs.
5. Apply the identical compiler, current coupling, switching rule, and path inverse to fresh `Q+[t]P`, preserve every path/source ambiguity, and subtract `t`.
6. Accept only `[x]P=Q`, charging graph construction, normalization, currents, path enumeration, source output, failed endpoints, target replay, verification, and memory.

## Full rho/BSGS cost model

Rho has expected time exponent `1/2`; BSGS has time and memory exponents `1/2`.
Let graph/current setup time and memory be `N^a,N^a_m`, reciprocal relation and target
densities `N^delta,N^delta_t`, one exact paired-current switching/source inverse
`N^q,N^q_m`, independent-rank gain `N^r`, source/path output and ambiguity `N^o,N^u`,
and factor-log completion `N^ell,N^ell_m`.  Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Vertices, edges, couplings, current multiplicities, normalization, exact sampling/counting retries,
duplicate-current state, switched paths, source output, relation rows, factor logs, masked descent,
verification, and peak state are charged.  Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

Random-current switching assumes a supplied graph, couplings, and named source vertices.  Making
those vertices distinguish factor points or point tuples reinstates the explicit source-incidence
deck; quotienting away the labels leaves only correlations and connectivity events.  The switching
lemma is an exact reindexing of sums over currents, not a canonical selector of one underlying path
or elliptic preimage.  Exact normalization, conditional generation, or enumeration of all relevant
currents and paths can be exponential and can reproduce the original search.

## Proof track

Construct a compact source-blind current graph, prove that exact switching canonically and completely
returns point-labelled sources on every stratum, and establish complete `lambda,mu<=0.45`.

## Disproof track

Prove that any correct graph compiler factors through explicit point-labelled incidences, exhibit
equal switched correlations with different elliptic source fibres, or show normalization, current/path
enumeration, output, ambiguity, or either complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: small supplied Ising graphs whose correlations, current sources, switched connections, and paths are independently exhaustively enumerated.
- Negative controls: vertex-label permutations, quotient graphs, high-temperature expansions, IDEA-050/079/102/213/225, IDEA-240 Bethe loop series, P1434, rho, and BSGS.

## Quantitative promotion and falsification gates

Reopening requires a source-blind graph and exact current procedure of exponent at most `0.45`,
canonical all-source recall with zero false points, no source-labelled edge deck, full factor-log rank,
100 blind descents at each of two largest future toy sizes, and complete `lambda,mu<=0.45`.  Any
explicit point-source graph, switching collision, current/path/output exponent at least `0.50`, or
complete exponent at least `0.50` falsifies this version.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-238/random_current_source_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-238/current_switching_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-238/independent_random_current_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-238/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is a novelty-unverified merged/scoped-negative high-risk hypothesis.  A correct current
representation, switching identity, connection event, valid relation, or recovered toy scalar is not
a complete generic ECDLP algorithm, crypto-scale validation, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-238/random_current_source_theorem.md` proving a compact endpoint current graph with canonical point-source paths or a graph/switching source-deck no-go.
