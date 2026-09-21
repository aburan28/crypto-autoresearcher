# ECDLP-IDEA-370 — Spectral-sparsification source router

## Status and claim labels

- Class: `representation`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_sparsifier_requires_explicit_source_incidence_and_loses_singleton_exactness`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; preserving quadratic forms of a supplied graph is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-derived relation-incidence graph admits a source-free spectral sparsifier whose restricted quadratic forms decide exact relation-fibre nonemptiness and replay one labelled source tuple within the P1553 gates.

## Mechanism-new operation

The screened operation is **replace a dense relation-incidence graph by a leverage-score or barrier-method spectral sparsifier, query restricted Laplacian forms, and self-reduce to one source edge**. It is distinct only if the graph and leverage oracle are constructed without source enumeration, arbitrary deck restrictions preserve exact zero-versus-nonzero fibres, and witness replay is charged rather than inferred from approximate energy.

## Assumptions

1. A public endpoint rule exposes graph incidence without listing relation tuples.
2. A subgate number of weighted edges preserves exact restricted nonemptiness, not merely every cut or quadratic form up to multiplicative error.
3. One target-independent sparsifier supports arbitrary pairwise-disjoint deck restrictions and fresh targets without source-sized rebuilds.
4. Restricted decisions self-reduce to one exact signed tuple in charged output time on every stratum.
5. Incidence generation, leverage estimation, sampling, precision, updates, output, rank, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`source_incidence_Laplacian | leverage_or_barrier_spectral_sparsifier | quadratic_form_preservation | exact_restricted_edge_nonemptiness | source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H663`; low-rank public kernels remain hypothetical and do not provide an exact source section.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`; recall-preserving compression remained full pair-state rank.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1420-ZERO-PRODUCT-NO-PROMOTION`; exact zero tests retained the full outer-pair surface.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; constructing a source-resolving circuit is the central missing operation.
5. `inputs/ledger_inventory.json` — imported `ECFG-H676`; public source generation and target batching remain unconstructed.

## Closest primary literature

- Batson, Spielman, and Srivastava, [Twice-Ramanujan Sparsifiers](https://doi.org/10.1137/090772873), gives spectral sparsifiers for a supplied weighted graph.
- Spielman and Srivastava, [Graph Sparsification by Effective Resistances](https://arxiv.org/abs/0803.0929), samples supplied edges using effective-resistance information.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations but no source-free incidence graph or exact sparsifier section.

No checked source gives exact restriction-stable source recovery for elliptic relation fibres; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor decks, endpoint incidence rule, sparsifier construction, precision, restriction protocol, masks, and verifier.
2. Construct a target-independent weighted sparsifier without enumerating relation-source edges or attaching scalar labels.
3. On known-log targets, decide restricted nonemptiness, bisect all source coordinates, replay the recovered tuple by group addition, and record all traffic.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply the unchanged sparsifier protocol to fresh scalar-blind `Q+[t]P` targets with charged target updates.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge incidence construction, leverage scores, sampled edges, precision, restrictions, output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Spectral sparsification starts from explicit edges and preserves energies only approximately. The missing object is precisely the source-incidence graph, while a rare singleton relation can be deleted without materially changing a global quadratic form. Exact correction or restriction-stable witness recovery restores the incidence table and merges this route with graph/Laplacian, cut, and low-rank controls in IDEAs 077, 203, 236, 348, and 369.

## Proof track

Construct the endpoint-only incidence and prove an exact zero/nonzero and witness-preservation theorem under every allowed restriction, together with complete exponents at most `0.45`.

## Disproof track

Give two relation graphs with indistinguishable permitted sparsifier data but different singleton restricted fibres, or lower-bound incidence construction/exact correction by `B^3`.

## Positive and negative controls

- Positive: supplied graphs with planted high-conductance relation clusters and separately labelled source edges.
- Negative: a singleton planted edge, source-permuted incidence, equal-energy graphs with different witnesses, arbitrary deck restrictions, and blind targets.
- Baselines: IDEAs 077/203/236/348/369, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only incidence, exact restriction-stable nonemptiness and source replay, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on explicit source edges, a deleted or invented singleton witness, source-sized exact correction, one missed stratum, `B^3` traffic, or either exponent at least `0.50`.
- A good spectral approximation on a supplied toy graph is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-370/exact_sparsifier_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-370/singleton_edge_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-370/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-370/cost_analysis.md`

## Interpretation boundary

This rejects the screened explicit-graph route, not spectral sparsification. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. Approximate energy preservation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-370/exact_sparsifier_obligations.md` and prove whether any endpoint-only sparsifier can preserve singleton restricted fibres without source incidence.
