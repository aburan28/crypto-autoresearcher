# ECDLP-IDEA-141 — Unambiguous-rectangle source factorization

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_decomposable_compilation_characterization`
- Cohort: `20260717-h`
- Evidence scale: theorem/semantic audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: prospective measurements are `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a small rectangle cover, exact membership answer, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

The forward-two/backward-three source incidence for every target has a target-uniform unambiguous communication-rectangle cover of sub-rho total description size. Each rectangle is constructed directly from compact elliptic equations before source leaves exist and includes exact left/right unranking maps, so intersecting rectangles enumerates all signed five-source tuples for rank and blind descent.

## Mechanism-new operation

The operation is **pre-leaf unambiguous rectangle construction with source unranking**. Rather than compile a general logical circuit, it would give an explicit algebraic cover of `A_2 x A_3` whose rectangles have disjoint accepted supports and compact source maps.

Semantic review merges this record into IDEA-135's source-faithful decomposable compilation lane. Deterministic decomposable circuits are assembled from precisely such disjoint source-block rectangles; a small explicit cover would be evidence for IDEA-135, while a cover built from source lists is the P1510/P1477 input. Keeping this record as a separate active mechanism would double-count the same pre-leaf operation.

## Assumptions

1. Public `E,<P>,N,Q,F`, `B=N^beta`, and signed/order/projective semantics are frozen.
2. Rectangles are computed from compact equations without enumerating `A_2`, `A_3`, accepted pairs, or scalar indices.
3. The cover is unambiguous on accepted tuples, complete on multiplicity, and carries exact source unranking maps.
4. Construction, description, queries, output, rank, factor logs, blind descent, and memory are charged.
5. One target-independent rule applies to known-log and fresh masked targets.

## Semantic fingerprint

`forward_backward_relation_matrix | pre_leaf_unambiguous_rectangles | disjoint_accepted_cover | exact_left_right_source_unranking | target_uniform_blind_descent`

This is the rectangle-level characterization of IDEA-135, not an independent mechanism after semantic deduplication.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the unresolved public source-fiber/transposed-join operation.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where complete value matrices and fixed tensor blocks remain full rank.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, which sets the strict complete-query exponent boundary.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, where source-distinct forward/backward states exceed the gate.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, where exact one-transition compression becomes dense on source-complete composition.

## Closest primary literature

- Yao, [Some complexity questions related to distributive computing (Preliminary Report)](https://doi.org/10.1145/800135.804414), establishes the communication-complexity framing behind rectangle covers.
- Pipatsrisawat and Darwiche, [A Lower Bound on the Size of Decomposable Negation Normal Form](https://doi.org/10.1609/aaai.v24i1.7600), connects structured decomposable circuits and partition/width lower bounds.
- Yannakakis, [Expressing combinatorial optimization problems by linear programs](https://doi.org/10.1016/0022-0000(91)90024-Y), relates factorization/rectangle structure to compact representations, but not elliptic source construction.

No checked source gives the explicit elliptic cover. Novelty remains unverified, while its mechanism is already represented by IDEA-135.

## Complete factor-base-to-target-descent path

1. Freeze inputs, left/right source partitions, cover construction, unranking, and independent verifier.
2. Construct the target-independent rectangle family before any source frontier is materialized.
3. Specialize known-log targets, enumerate each accepted rectangle's exact tuples, and verify elliptic addition.
4. Reach rank `B`, solve and verify factor logs.
5. Specialize fresh masked targets, enumerate all rectangle sources and scalar candidates, and accept only `[x]P=Q`.
6. Charge construction, rectangle bytes, unranking, output, rank, linear algebra, descent, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time and constant state; BSGS costs `N^(1/2+o(1))` time/memory. Let cover construction/memory be `N^a,N^a_m`, cover size `N^c`, target filtering/unranking time and working memory `N^q,N^q_m`, inverse densities `N^delta,N^delta_t`, output `o`, ambiguity `u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,c,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
Every rectangle boundary and source map is charged. Toy cover counts remain model-bound.

## Likely fatal obstruction

Generic source provenance may give high unambiguous rectangle/communication complexity. Rectangles that retain only endpoint membership merge many source tuples; exact unranking decorates them with the source lists they were meant to avoid. This is also the same central question as source-faithful d-DNNF compilation, so maintaining a separate lane would duplicate evidence and contracts.

## Proof track

Any explicit cover theorem should be recorded as the rectangle construction inside IDEA-135, with exact unranking and complete `lambda,mu<=0.45`.

## Disproof track

Prove a rectangle-cover/communication lower bound, show labels require explicit source leaves, or show the construction is a d-DNNF compiler instance. The last reduction establishes the current merge.

## Positive and negative controls

- **Positive control:** functions with known small unambiguous rectangle partitions and source unranking.
- **Positive control:** exhaustive tiny elliptic relation matrices.
- **Negative control:** random matrices matched for density, membership-only rectangles, and rectangles decorated after source enumeration.
- **Negative control:** P1477 states, P1478 composition, and d-DNNF circuits from IDEA-135.
- **End-to-end control:** rho/BSGS and blind targets with cover construction charged.

## Quantitative promotion and falsification gates

This record is merged/rejected into IDEA-135. A rectangle theorem can promote only that existing lane after exact source completeness and `lambda,mu<=0.45`; it does not receive a second contract. Any explicit source list, ambiguity, or complete exponent at least `0.5` falsifies the proposed compact cover.

## Artifact plan

- Semantic merge note: `ideas/artifacts/ECDLP-IDEA-141/rectangle_dDNNF_equivalence.md`
- Prospective lower bound: `ideas/artifacts/ECDLP-IDEA-141/rectangle_lower_bound.md`
- Frozen controls: `ideas/artifacts/ECDLP-IDEA-141/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-141/cost_analysis.md`

No artifact exists.

## Interpretation boundary

This is preserved merged/rejected evidence. All prospective tests are toy, novelty is unverified, and costs are heuristic/model-bound. A compact membership cover is not source recovery or an ECDLP breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-141/rectangle_dDNNF_equivalence.md` mapping each unambiguous source rectangle to the deterministic/decomposable nodes of IDEA-135 and recording any genuinely non-equivalent operation under a fresh ID.
