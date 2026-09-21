# ECDLP-IDEA-077 — Kron–Schur boundary-response descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `merged_rejected`
- Evidence scale: `toy` exact-matrix preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an exact Schur complement or response minor is not an ECDLP break.

## Falsifiable hypothesis

An implicitly generated partial-sum graph has factor-base atoms and target `R` on its boundary. Exact Kron/Schur elimination of internal partial sums yields a sparse boundary response matrix with a distinguished minor whose nullvector identifies an endpoint-to-target witness; back-substitution returns every source point. If fill, factorization, response extraction, output, relation rank, and blind descent are all sub-rho, this yields a complete ECDLP path.

## Mechanism-new operation

The operation is **exact internal-state elimination followed by a source-resolving boundary response and ancestry back-substitution**. Sparse linear algebra on a materialized incidence table, a determinant that only counts walks, a post-hoc row filter, or faster evaluation of unchanged pair states is a control. Novelty depends on a graph construction whose response stays sparse and whose inverse retains sources.

## Assumptions

1. A public partial-sum graph can be generated implicitly with fewer than `N^(1/2)` paid states/edges.
2. Boundary vertices correspond to exact factor-base atoms and the masked target.
3. Elimination order is target-independent and produces sub-rho fill.
4. A response minor is biconditional for a valid decomposition and returns a bounded witness list.
5. Elimination ancestry back-substitutes exact points/signs.
6. Graph construction, all fill, factorization, output, `N^beta` rows, rank, target descent, and memory are charged.

## Semantic fingerprint

`implicit_partial_sum_graph | exact_Kron_Schur_elimination | sparse_boundary_response_minor | ancestry_source_backsubstitution | relation_rank_and_blind_target_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, the closest sparse-transition composition gap.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, the positive one-transition primitive.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where an exact matrix remains full rank.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, the exact source-fiber join boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, where avoiding triple advice restores cubic target work.

## Closest primary literature

- Dörfler and Bullo, [Kron reduction of graphs with applications to electrical networks](https://arxiv.org/abs/1102.2950), develops Schur boundary responses, not elliptic witness extraction.
- Giusti, Lecerf, and Salvy, [A Gröbner-free alternative for polynomial system solving](https://doi.org/10.1006/jcom.2000.0571), supplies a nearby elimination/solution-count boundary.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies the underlying decomposition equations but no sparse response graph.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,m`, graph vertices/edges/weights, boundary, elimination order, and exhaustive witness reference.
2. Generate the graph implicitly and prove path/decomposition correspondence on complete toy cases.
3. Perform exact Schur elimination, retain every pivot/fill edge, and compute the specified boundary minor.
4. Back-substitute every null response to exact source points and verify the elliptic sum.
5. Collect enough randomized source-labelled rows, solve factor logs, and verify them.
6. Repeat on masked blind targets, recover a factor-base decomposition, unmask its scalar, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho has time exponent `1/2`; BSGS has time and memory exponent `1/2`. Let graph size exponent be `g`, fill exponent `f`, exact factorization exponent `k`, factor-base exponent `beta`, relation/target density exponents `delta,delta_t`, response/source output `o`, linear algebra `ell`, and memory `mu`. The complete exponent is `lambda=max(g,f,k,beta+delta+k+o,ell,delta_t+k+o)`. Graph/fill storage is peak memory, not amortized setup.

## Likely fatal obstruction

Kron reduction is exact elimination on the same partial-sum graph already occupied by sparse-transition, response, and reporter lanes. It aggregates internal walks, typically densifies the boundary response, and forgets path identities. The natural graph has `Omega(N)` group-state vertices; exact back-substitution reconstructs all paths and restores their output cost. Without a new graph theorem, this is a solver/reporting backend for `038/056/066/071/083` and `P1478`, not a new obstruction-removing operation.

## Proof track

Construct a graph family and elimination order with provably sub-sqrt state/fill, prove the response-minor/witness biconditional and exact ancestry lift, then bound full relation/descent costs.

## Disproof track

Show graph size or fill exponent at least `1/2`, find distinct source paths with the same response, or show source back-substitution enumerates `N^(1/2)` paths.

## Positive and negative controls

- Electrical-network graphs with known sparse Kron reductions.
- Planted unique-path and many-path partial-sum graphs.
- Nested-dissection, random, and forbidden witness-aware elimination orders.
- Exact full adjacency/Schur computation on tiny cases.
- Determinant-only/counting controls.
- Blind masked targets and matched rho/BSGS baselines.

## Quantitative promotion and falsification gates

The theorem gate requires exact path/source correspondence and upper symbolic fill below `N^(1/2)`. A later promotion gate requires zero source errors, 1,000 independent rows, 100 blind descents, and upper 95% `g,f,lambda,mu<=0.45`. Falsify if lower 95% fill/graph/output exponent is at least `0.50` or response ambiguity has that exponent.

## Artifact plan

- Graph theorem: `ideas/artifacts/ECDLP-IDEA-077/boundary_response.md`
- Graph builder: `ideas/artifacts/ECDLP-IDEA-077/partial_sum_graph.sage`
- Elimination: `ideas/artifacts/ECDLP-IDEA-077/kron_descent.sage`
- Verifier: `ideas/artifacts/ECDLP-IDEA-077/verify_response_sources.py`
- Analysis: `ideas/artifacts/ECDLP-IDEA-077/analysis.md`

## Interpretation boundary

This deferred idea is toy, heuristic, model-bound, and novelty-unverified. A sparse toy Schur complement or correct response identity is not a cryptanalytic performance claim.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-077/kron_collision_boundary.md` deriving the Schur response and full source-backsubstitution cost on the frozen partial-sum graph and mapping it to the occupied transition/reporter lanes.
