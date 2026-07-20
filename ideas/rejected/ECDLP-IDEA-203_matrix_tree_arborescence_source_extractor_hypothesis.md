# ECDLP-IDEA-203 — Matrix-tree arborescence source extractor

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_laplacian_requires_explicit_source_transition_graph`
- Cohort: `20260718-d`
- Evidence scale: literature and input-size audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective finite checks are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a determinant, forest count, or valid path is not an ECDLP break.

## Falsifiable hypothesis

The exact partial-sum/source relation structure has a compact weighted directed graph whose all-minors Laplacian determinants encode endpoint-conditioned arborescences. Logarithmic derivatives or determinant self-reduction can extract exact signed five-leaf paths and yield enough independent relations and masked descents below rho and BSGS.

## Mechanism-new operation

The proposed operation is **all-minors matrix-tree aggregation plus endpoint-conditioned arborescence source extraction**. It differs from ordinary path enumeration by claiming that determinant identities keep enough ancestry to self-reduce to leaves. The audit rejects the formulation because the Laplacian must first contain every source-distinct transition; the determinant counts forests of that supplied graph and loses which leaf tuple generated an endpoint.

## Assumptions

1. Public `E/F_p`, prime-order group of size `N`, factor base `B=N^beta`, and target are frozen.
2. A target-independent weighted graph/Laplacian of size at most `B^2.25` represents every exact signed five-source relation.
3. Edge weights and minors are constructed without `B^2/B^3` source-transition enumeration.
4. Determinant derivatives return every exact path, including repeats, cycles, infinity, and multiplicity.
5. Graph construction, determinant arithmetic, self-reduction, output, rank, factor logs, blind descent, and memory are charged.

## Semantic fingerprint

`elliptic_partial_sum_transition_graph | compact_weighted_Laplacian | all_minors_arborescence_determinant | endpoint_self_reduction_to_exact_leaves | blind_descent`

The fingerprint fails if the graph is explicitly source-distinct, if determinants only count paths, or if edges are joined to sources after evaluation.

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the lossless ancestry-edge floor.
2. `inputs/ledger_inventory.json` — imported `P1477`, the serial partial-sum state control.
3. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1435-STAGE1-GENERATOR-BATCH-B3-BOUNDARY`, the pair-only generator/cubic-query boundary.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, the aggregate-root/source-loss boundary.

## Closest primary literature

- Chaiken, [A combinatorial proof of the all minors matrix tree theorem](https://doi.org/10.1137/0603033), evaluates forest sums for a supplied weighted graph.
- Duval, Klivans, and Martin, [Simplicial matrix-tree theorems](https://arxiv.org/abs/0802.2576), extends determinant enumeration but still assumes the underlying incidence structure.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations rather than a compact source-transition Laplacian.

No checked primary source supplies the proposed graph constructor/source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the vertex/edge grammar, weights, endpoint minors, self-reduction rule, masks, and verifier.
2. Construct the compact target-independent Laplacian without explicit source transitions.
3. Evaluate known-log endpoint minors and self-reduce nonzero determinants to every exact signed source path.
4. Verify paths and preserve cancellations, cycles, repeated leaves, infinity, multiplicity, and empty endpoints.
5. Collect full-rank rows, solve and verify factor-base logs.
6. Apply identical minors and self-reduction to fresh masks `Q+[r]P`.
7. Substitute logs, subtract masks, retain ambiguity, and verify `[x]P=Q`.
8. Charge graph construction, determinant work, queries, output, rank, linear algebra, descent, verification, time, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup be `N^a,N^a_m`; reciprocal densities `N^delta,N^delta_t`; one minor query and source self-reduction `N^q,N^q_m`; ranked rows/query `N^r`; output and ambiguity `o,u`; and factor-log linear algebra `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; fast determinant evaluation of an uncharged explicit graph is invalid.

## Likely fatal obstruction

Matrix-tree theorems aggregate forests only after all weighted edges are supplied. An exact elliptic partial-sum graph needs `B^2` pair edges and `B^3` source-distinct middle transitions. Collapsing equal endpoints removes leaf ancestry; retaining separate edge variables recreates that deck. Log derivatives identify supplied edges, and conditioned determinant calls merely repeat the missing completion/source query.

## Proof track

Construct a source-biconditional Laplacian of size at most `B^2.25`, prove determinant self-reduction recovers all exact leaves without edge enumeration, and derive `lambda,mu<=0.45` through blind descent.

## Disproof track

Prove every lossless graph needs `Omega(B^3)` source-distinct edges, exhibit two source families with the same collapsed Laplacian/minors, reduce derivative access to explicit edge variables, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: a supplied labelled toy DAG with independently enumerated arborescences.
- Negative control: collapsed endpoint graphs whose determinants preserve counts but not leaf identities.
- Negative control: explicit source-edge Laplacians, conditioned path enumeration, dense resultants, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires target-independent graph size at most `B^2.25`, query at most `B^1.25`, 100% exact path/source recall, zero false tuples, no explicit source-edge deck, and `lambda,mu<=0.45`. `Omega(B^3)` edges, aggregate-only minors, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective graph-size theorem: `ideas/artifacts/ECDLP-IDEA-203/compact_laplacian_theorem.md`
- Prospective source inverse: `ideas/artifacts/ECDLP-IDEA-203/arborescence_source_inverse_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-203/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified algorithm analysis. Finite checks would be toy and projections heuristic and model-bound. A determinant, forest count, exact relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-203/compact_laplacian_theorem.md` proving a source-biconditional Laplacian with at most `B^2.25` encoded edges or proving that lossless endpoint ancestry forces `Omega(B^3)` source-distinct transitions.
