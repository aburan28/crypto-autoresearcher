# ECDLP-IDEA-217 — Stallings core-fold source router

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_source_word_or_endpoint_path_required`
- Cohort: `20260718-e`
- Evidence scale: primary-literature and group-theoretic audit only; no experiment ran
- Contract posture: none
- Scale labels: every prospective finite check is `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a folded core, membership proof, or valid path is not an ECDLP break.

## Falsifiable hypothesis

Elliptic factor atoms admit a public free-group word encoding whose five-sum law is subgroup membership. Stallings folding of an endpoint-derived graph would produce a bounded deterministic core path with an exact inverse to factor words, enabling factor logs and blind target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **Stallings core folding followed by deterministic endpoint-path inversion**. It merges/rejects because a homomorphism from the finite prime-cyclic group to a torsion-free free group is trivial; any nonhomomorphic word law needs source-dependent defect words, and folding a supplied graph merges rather than creates ancestry.

## Assumptions

1. Public curve/group/factor base `B=N^beta` and target are frozen with a target-independent finite word alphabet.
2. Endpoint words/graphs are constructed without source words, scalar labels, or an explicit lossless ancestry DAG.
3. Subgroup membership is biconditional with all signed five-source sums and its core path inverts exactly on every stratum.
4. Word length, defect data, graph construction, folding, inverse output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`elliptic_atoms_to_free_group_words | five_sum_subgroup_membership_law | Stallings_core_folding | deterministic_endpoint_path | exact_factor_word_inverse | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fiber generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`, the ancestry-edge floor.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the explicit source-word/edge boundary.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1477`, the serial source-state barrier.
5. `inputs/ledger_inventory.json` — imported `P1477`, the dense state-polynomial control.

## Closest primary literature

- Stallings, [Topology of finite graphs](https://doi.org/10.1007/BF02095993), gives folding and subgroup membership after a labelled graph/word system is supplied.
- Fox, [Free differential calculus I](https://doi.org/10.2307/1969736), is the nearest nonabelian word-ancestry control.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint relations without a word compiler.

No checked source supplies the elliptic five-sum word law and exact source inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze atom words, endpoint graph compiler, subgroup law, fold order, path inverse, masks, and verifier.
2. Prove the word-membership/source biconditional and build the graph without source paths.
3. For known endpoints, fold the graph, enumerate accepted core paths, invert to exact signed points, and verify rows.
4. Collect full rank, solve and verify factor-base logarithms.
5. Repeat unchanged on fresh `Q+[t]P`, substitute logs, subtract `t`, retain ambiguity, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Rho and BSGS cost `N^(1/2+o(1))`; BSGS also uses that memory. With setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, graph/fold/source query `N^q,N^q_m`, rank gain `N^r`, output/ambiguity `N^o,N^u`, and factor-log work `N^ell,N^ell_m`,

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

All word and edge traffic is charged; both exponents must be at most `0.45`.

## Likely fatal obstruction

Any homomorphic map from finite prime-cyclic `G` to a free group is trivial because free groups are torsion-free. A nonhomomorphic map must carry source-dependent defect words. Folding only minimizes a supplied labelled graph; it loses distinct histories, while an exact inverse restores the explicit edge/source-word deck.

## Proof track

Give a bounded nonhomomorphic five-sum membership law with source-free endpoint compiler and exact all-strata inverse, proving complete `lambda,mu<=0.45`.

## Disproof track

Prove the iff law forces a Freiman/homomorphic restriction and hence triviality, exhibit required defect/source words, lower-bound core edges by `B^3`, lose one source, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive control: supplied finitely generated subgroups and planted source words with independently checked folded cores.
- Negative controls: homomorphic encodings of finite cyclic groups, shuffled defect words, explicit ancestry DAGs, Fox/automata routers, rho, and BSGS.

## Quantitative promotion and falsification gates

This version is merged/rejected. Reopening requires graph/state at most `B^2.25`, query at most `B^1.25`, 100% exact word/source recall, zero false paths, no defect/source deck, post-aggregation rank `B`, and `lambda,mu<=0.45`. Homomorphic triviality, source-word dependence, one lost source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective encoding: `ideas/artifacts/ECDLP-IDEA-217/stallings_encoding_spec.md`
- Prospective core gate: `ideas/artifacts/ECDLP-IDEA-217/core_size_gate.md`
- Prospective fixtures: `ideas/artifacts/ECDLP-IDEA-217/fixtures.json`
- Prospective verifier: `ideas/artifacts/ECDLP-IDEA-217/independent_verifier.py`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-217/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is novelty-unverified merged/rejected mechanism analysis. Finite checks would be toy and projections heuristic and model-bound. A folded core, membership proof, valid relation, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-217/stallings_encoding_spec.md` for the symbolic signed two-plus-three transition and decide whether a bounded source-free word law exists or a homomorphic/defect-word obstruction closes it.
