# ECDLP-IDEA-223 — Gammoid-linkage source router

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_linkage_graph_is_the_source_transition_deck`
- Cohort: `20260718-f`
- Evidence scale: primary-literature and semantic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a gammoid representation, determinant, or valid linkage is not an ECDLP break.

## Falsifiable hypothesis

Exact signed elliptic decompositions are the vertex-disjoint linkages of a compact endpoint-derived directed graph. A strict-gammoid representation would test and unrank every linkage to exact factor points, providing relation rows and blind target descent below rho and BSGS.

## Mechanism-new operation

The claimed operation is **endpoint-to-gammoid compilation followed by disjoint-linkage source unranking**. It merges/rejects because a gammoid is defined from a directed graph with named starts and sinks. Making its paths biconditional with elliptic sources constructs the missing pair/triple transition graph; determinants test aggregate linkage feasibility and do not return all exact paths without source-sized state.

## Assumptions

1. Public `E/F_p`, prime-order subgroup, factor base `F` of size `B=N^beta`, and graph grammar are target-independent.
2. The directed graph has sub-square-root construction/state and is not an explicit source-completion graph.
3. Linkages are biconditional with every signed source tuple and unrank canonically through repeats and cancellation.
4. Graph, determinant, path output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`elliptic_atoms_as_linkage_terminals | endpoint_directed_graph | strict_gammoid_determinant | vertex_disjoint_path_unranking | exact_point_sources | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the public source-fiber generator gap.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`, the exact-source predicate boundary.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the arithmetic source-generator boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless transition-edge floor.
5. `inputs/ledger_inventory.json` — imported `TRANSFER-NR-004`, the Plücker/incidence aggregation control.

## Closest primary literature

- Mason, [On a class of matroids arising from paths in graphs](https://doi.org/10.1112/plms/s3-25.1.55), defines the path-linkage matroid setting.
- Ingleton and Piff, [Gammoids and transversal matroids](https://doi.org/10.1016/0095-8956(73)90031-2), characterizes gammoids through supplied graph/matroid data.
- Ardila, [Transversal and cotransversal matroids via the Lindström lemma](https://arxiv.org/abs/math/0605629), gives determinant representations from supplied path networks.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies relation equations but no compact linkage graph.

No checked source constructs the endpoint graph and exact source unranker. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the graph grammar, starts/sinks, weights, linkage test, path inverse, masks, and verifier.
2. Build the endpoint graph without pair/triple/source enumeration and compute the gammoid representation.
3. Enumerate every accepted linkage, return exact signed factor points, and verify each elliptic row.
4. Collect full rank, solve and verify all factor-base logarithms.
5. Rebuild under the identical rules for fresh `Q+[t]P`, unrank target linkages, substitute logs, and subtract `t`.
6. Preserve path/cancellation ambiguity and accept only `[x]P=Q`, charging graph and output memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. With graph setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, linkage test plus exact unranking `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log costs `N^ell,N^ell_m`, the complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All vertices, edges, determinant entries, path witnesses, and outputs are charged. Promotion requires `lambda,mu<=0.45`.

## Likely fatal obstruction

The directed graph is not inferred by gammoid theory; it is the input. Edges that preserve exact elliptic ancestry are precisely pair/source transitions, and named terminals carry factor labels. The determinant can cancel or aggregate path families, while outputting every path reinstates their full traffic. Thus the representation consumes rather than creates the endpoint-to-source operation.

## Proof track

Give a sub-square-root endpoint graph compiler and prove linkage/source biconditionality, all-path unranking, and `lambda,mu<=0.45`.

## Disproof track

Show edge construction needs the source-completion relation, exhibit different linkages with the same determinant data, or prove graph/path state reaches square-root scale.

## Positive and negative controls

- Positive control: a planted directed network with supplied disjoint source paths and an independently checked gammoid matrix.
- Negative controls: label-erased terminals, determinant-only output, IDEA-137/203/206/212, explicit pair graphs, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires a graph compiler outside IDEA-206, graph and query exponents at most `0.45`, 100% exact-path recall, zero false paths, and complete `lambda,mu<=0.45`. Source-transition edges, determinant cancellation, or either exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective theorem: `ideas/artifacts/ECDLP-IDEA-223/gammoid_source_graph_theorem.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-223/linkage_collision_fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-223/independent_linkage_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-223/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected algorithm analysis. Finite checks would be toy and projections heuristic and model-bound. A gammoid determinant, valid linkage, relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-223/gammoid_source_graph_theorem.md` deriving a source-free endpoint graph or proving that every exact linkage edge set materializes the occupied source-transition deck.
