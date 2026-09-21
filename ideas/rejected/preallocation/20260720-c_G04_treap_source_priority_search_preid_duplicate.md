# Pre-ID duplicate draft — Treap source-priority search

## Status and claim labels

- Prospect: 20260720-c-G04; no canonical ECDLP idea ID was allocated
- Class / risk / lane: randomized_priority_search_tree / conservative / general pre-ID screen
- State: merged_rejected_supplied_source_keys_and_random_priority_only
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; expected-cost claims are heuristic, model-bound, and novelty-unverified for the ECDLP transplant
- Breakthrough claim: none; expected logarithmic dictionary search is not scalar recovery.

## Falsifiable hypothesis

Store endpoint-derived partial-source keys in a treap with public random priorities. Expected-balanced split/merge operations would maintain restricted source dictionaries, replay exact signed occurrences, and support relation collection and blind target descent below rho and BSGS.

## Mechanism-new operation

A treap is binary-search ordered by supplied keys and heap ordered by independent priorities; rotations give expected logarithmic search/update. It counts only if exact elliptic keys are constructed without source enumeration, priority randomness is target-independent, and a found key lifts to signed occurrences. Randomizing an explicit source dictionary is a control.

## Assumptions

1. Public endpoint keys have exact equality and a fixed total order.
2. Key construction, priority sampling/seeds, rotations, splits/merges, failures, restrictions, replay, rank, logs, descent, bit time, and memory are charged.
3. Priority randomness is independent of targets and source validity.
4. Nodes preserve occurrence provenance through updates and canonical restrictions.
5. The same tree and distribution serve fresh blind targets.

## Semantic fingerprint

public_ordered_endpoint_keys | treap_random_priority_rotations | exact_restricted_key_search | treap_node_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact source-recovery residual.
2. ideas/rejected/preallocation/20260720-a_E07_skiplist_source_order_index_preid_duplicate.md — random levels do not create source keys.
3. ideas/rejected/preallocation/20260719-a_A11_fks_perfect_hash_source_dictionary_preid_duplicate.md — expected lookup starts after source-bearing keys exist.
4. ideas/rejected/preallocation/20260719-c_C11_cuckoo_hash_source_peeling_preid_duplicate.md — randomized placement preserves a supplied key set.
5. ideas/rejected/preallocation/20260720-b_F12_fusion_tree_endpoint_predecessor_preid_duplicate.md — word-level predecessor is likewise a backend after key construction.

## Closest primary literature

- Seidel and Aragon, [Randomized search trees](https://doi.org/10.1007/s004539900061), analyzes randomized search trees for supplied ordered keys.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations but no exact ordered source dictionary.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies elliptic keys, source inversion, or a fresh-target guarantee; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, key/order, priority distribution and seeds, update/restriction rules, provenance, and verifier.
2. Construct the target-independent key set/tree within B^(9/4+o(1)) without enumerating source matches.
3. For known-log R, use exact restricted searches to replay A_i,epsilon_i in bounded bisection; verify point equality before recording an unknown-log row.
4. Collect at least max(d_FB+32,1,000) verified rows, retain all misses/dependencies, require rank d_FB, then solve factor logs.
5. Reuse unchanged state for Q+[t]P, recover a tuple, compute x, and verify [x]P=Q.
6. Charge key generation, comparisons, random bits, rotations, splits/merges, restrictions, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Let n be stored keys, U updates/restrictions, Q searches, C_key key/comparison work, R_rot rotations, and C_inv replay. Expected supplied-treap work is O((U+Q)log n), state O(n), with O(n) worst-case height. Set a=log_N(T_key_build+U C_key+R_rot C_rot), a_m=log_N(M_keys+n), q=log_N(Q_R(C_search+C_inv)+T_replay), and q_m=log_N(M_tree+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Expected and one-sided tail costs are both reported. Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

The random priorities balance a supplied dictionary; they do not reveal which endpoint combinations form a source. Exact keys reintroduce the source catalogue, while coarse keys collide. Expected height cannot repair missing information or exact negative semantics. This merges with E07/A11/C11/F12.

## Proof track

Prove compact endpoint key construction, exact restriction/source biconditional, target-independent tail bounds, provenance, rank, and blind descent.

## Disproof track

Find a public-key collision with different source validity, or show dictionary construction requires enumerating compatible tuples.

## Positive and negative controls

- Positive: supplied labelled keys with independent priorities.
- Negative: adversarial priority seeds, colliding endpoint keys, absent keys, empty/singleton restrictions, exceptional and blind targets.
- Baselines: E07/A11/C11/F12, deterministic balanced trees, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only keys, exact source replay, seed-independent tail gate, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing key, false lookup, provenance collision, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g04_key_collision_audit.md
- ideas/rejected/preallocation/artifacts/20260720-c/g04_priority_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g04_cost_analysis.md

## Interpretation boundary

This rejects the elliptic treap transplant, not randomized search trees. Expected logarithmic access or one relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g04_key_collision_audit.md; do not create it under this retired pre-ID screen.
