# Pre-ID duplicate draft — Splay-tree source access

## Status and claim labels

- Prospect: 20260720-c-G02; no canonical ECDLP idea ID was allocated
- Class / risk / lane: self_adjusting_search_tree / conservative / general pre-ID screen
- State: merged_rejected_supplied_ordered_source_dictionary
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; locality extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; an amortized dictionary speedup is not an ECDLP speedup.

## Falsifiable hypothesis

Order pair-endpoint and singleton-source keys so that repeated relation and restriction queries have locality. Splaying accessed keys to the root would amortize exact restricted source lookup, retain signed occurrence records, and support relation collection and fresh blind descent below rho and BSGS.

## Mechanism-new operation

A splay tree performs zig, zig-zig, and zig-zag rotations after each access and proves an amortized access lemma for a supplied ordered key set. It counts only if public elliptic endpoints provide the order and queried keys without pre-enumerated sources, and successful nodes replay exact occurrences. Replacing a balanced tree in an explicit table is a backend control.

## Assumptions

1. Public endpoint keys have a target-independent total order and exact equality semantics.
2. Key generation, comparisons, rotations, restrictions, failed searches, replay, rank, logs, descent, bit time, and memory are charged.
3. Locality follows from target-independent structure rather than post-hoc query ordering.
4. Each node retains complete signed source provenance under rotations and restrictions.
5. Fresh blind targets receive the same access guarantee without training on their scalar.

## Semantic fingerprint

public_ordered_endpoint_keys | splay_rotation_access_lemma | exact_restricted_lookup | dictionary_node_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact endpoint-to-source frontier.
2. ideas/rejected/preallocation/20260719-b_B09_link_cut_tree_source_path_router_preid_duplicate.md — dynamic-tree navigation assumes supplied labelled edges.
3. ideas/rejected/preallocation/20260720-a_E07_skiplist_source_order_index_preid_duplicate.md — randomized ordered indexing still requires source keys.
4. ideas/rejected/preallocation/20260720-b_F12_fusion_tree_endpoint_predecessor_preid_duplicate.md — faster predecessor does not construct an exact source key.
5. ideas/rejected/preallocation/20260719-a_A11_fks_perfect_hash_source_dictionary_preid_duplicate.md — dictionary lookup begins after exact source-bearing keys exist.

## Closest primary literature

- Sleator and Tarjan, [Self-adjusting binary search trees](https://doi.org/10.1145/3828.3835), proves amortized bounds for accesses to a supplied ordered dictionary.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but no ordered exact source keys.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic key compiler or source-faithful locality theorem; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, endpoint key, order, rotation policy, restriction rule, provenance record, and verifier.
2. Construct a target-independent tree within B^(9/4+o(1)) without listing pair-pair-singleton source matches.
3. For R=[kappa]P, use exact restricted searches to replay labelled A_i,epsilon_i in at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify point equality before recording the unknown-log row.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, preserve dependencies and misses, and solve factor logs only after rank passes.
5. Reuse unchanged state for R=Q+[t]P, replay a tuple, compute and verify the scalar x.
6. Charge key construction, all comparisons/rotations, unsuccessful searches, restrictions, replay, density, rank, logs, blind descent, bit time, and peak memory.

## Full rho/BSGS cost model

Let n be stored keys, m the complete access sequence, C_key comparison/key work, R_rot rotations, Q_R restriction queries, and C_inv replay. Splaying costs O((m+n)log n) amortized over a supplied sequence but one access can cost O(n). Set a=log_N(T_key_build+n C_key), a_m=log_N(M_keys+n), q=log_N(Q_R(C_access+C_inv)+R_rot C_rot+T_replay), and q_m=log_N(M_tree+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m terms,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Both the total sequence and worst fresh-target access are charged. Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

Splaying exploits locality among already represented ordered keys. Exact endpoint keys either omit source ancestry and admit false matches, or materialize the source dictionary that P1553 lacks. An adversarial fresh target need not share trained locality. This is a backend substitution for B09/E07/F12/A11.

## Proof track

Prove endpoint-only key construction, target-uniform dynamic-finger locality, exact restriction/source biconditional, rank, and blind descent under complete costs.

## Disproof track

Show one pair of source tuples with the same public key but different validity, or a fresh-target access sequence with source-sized searches.

## Positive and negative controls

- Positive: a supplied ordered dictionary with Zipf-local labelled queries.
- Negative: shuffled access order, equal endpoint keys with different ancestry, absent keys, empty/singleton restrictions, and blind targets.
- Baselines: balanced trees, B09/E07/F12/A11, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with public keys/order, exact provenance under restrictions, worst fresh-target cap, rank d_FB, 100 blind descents, and lambda,mu<=0.45.
- Falsify on one source-bearing key, provenance collision, post-hoc locality schedule, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g02_key_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g02_access_sequence_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g02_cost_analysis.md

## Interpretation boundary

This rejects the elliptic lookup transplant, not splay trees. Fewer rotations or a correct lookup is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g02_key_provenance.md; do not create it under this retired pre-ID screen.
