# Pre-ID duplicate draft — PATRICIA radix source trie

## Status and claim labels

- Prospect: 20260720-d-H01; no canonical ECDLP idea ID was allocated
- Class / risk / lane: compressed_prefix_dictionary / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_key_bits_and_occurrence_leaves
- Evidence: complete live ledger/corpus and checked primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; correctness, a relation, or native algorithm performance is not an ECDLP result.

## Falsifiable hypothesis

Encode partial signed sources as public endpoint bit strings; PATRICIA path compression would answer exact restricted existence, replay one labelled tuple, complete logs, and descend fresh blind targets below rho/BSGS.

## Mechanism-new operation

PATRICIA retains discriminating bit positions for a supplied key set. It counts only if endpoint-derived keys exist before source incidence and compressed leaves lift exactly to signed occurrences; indexing serialized source tuples is a control.

## Assumptions

1. Endpoint-only keys and exact occurrence buckets can be built for the permitted B^2 pair tables without tuple loss.
2. Compressed branches preserve signed, repeated, exceptional, empty, and restricted cases, including every occurrence sharing a key.
3. Key construction, branch tests, replay, rank, logs, descent, bit time, and state are charged.
4. Each leaf lifts to exact occurrences, not only an endpoint.
5. The same state serves known-log and fresh scalar-blind targets.

## Semantic fingerprint

public_endpoint_bit_key | PATRICIA_discriminating_path_compression | exact_restricted_membership | leaf_to_signed_occurrences | logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — live uncommitted P1553 R4 exact restricted common-factor frontier.
2. ideas/rejected/preallocation/20260719-a_A06_fm_index_backward_source_unranking_preid_duplicate.md — compressed text indexing starts from a source serialization.
3. ideas/rejected/preallocation/20260719-a_A11_fks_perfect_hash_source_dictionary_preid_duplicate.md — exact lookup consumes the source key set.
4. ideas/rejected/preallocation/20260720-b_F09_kmp_failure_link_source_matcher_preid_duplicate.md — prefix acceleration needs a supplied text.
5. ideas/rejected/preallocation/20260720-c_G01_hopcroft_dfa_source_partition_preid_duplicate.md — automaton compression does not create acceptance information.

## Closest primary literature

- Morrison, [PATRICIA—Practical Algorithm To Retrieve Information Coded in Alphanumeric](https://doi.org/10.1145/321479.321481), assumes supplied encoded keys.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not this source compiler.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required elliptic endpoint-to-source operation; ECDLP novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, exceptional charts, native state, restriction grammar, and independent point verifier.
2. Construct target-independent state from public endpoints within B^(9/4+o(1)) without enumerating source tuples or invoking Query2P1.
3. For R=[kappa]P, use exact restricted existence and charged replay to return labelled A_i and signs epsilon_i in at most 5 ceil(log_2 B)+O(1) positive/negative queries; verify sum_i epsilon_i A_i=[kappa]P before recording sum_i epsilon_i y(A_i)=kappa in unknown logs.
4. Let d_FB be the actual distinct factor-log dimension; retain failures/dependencies, collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, replay a tuple, compute x=sum_i epsilon_i log_P(A_i)-t mod N, and independently verify [x]P=Q.
6. Charge construction, restrictions, failed queries, replay, relation density, rank, log solve, descent, scalar verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For n keys of at most w bits, charge T_key plus O(nw) build, O(w) per query, and C_leaf replay: a=log_N(T_key+nw), a_m=log_N(M_key+nw), q=log_N(Q_R(w+C_leaf)+T_replay), q_m=log_N(M_trie+M_leaf).

For B=N^beta, beta=1/5, let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ambiguity/rebuild/error overhead, and ell,ell_m factor-log time/state:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/advice/state <=B^(9/4+o(1)), complete fresh work/workspace <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values require one-sided 95% upper bounds below empirical gates.

## Likely fatal obstruction

Duplicate-preserving B^2 pair-endpoint keys and backpointers are allowed and can be stored exactly in a PATRICIA trie. The failure is later: PATRICIA does not construct the target-dependent extendibility/restriction bits that select a compatible (u,v,a) source. Storing those bits requires Query2P1 or materializes the B^3 target-dependent pair-by-fifth traffic; compressing already-supplied keys changes neither bound.

## Proof track

Prove that endpoint-only target-dependent extendibility bits can be derived from the permitted duplicate-preserving B^2 pair keys, while replaying every occurrence in a selected bucket, without Query2P1 or B^3 pair-by-fifth traffic; then prove restriction-stable branching, exact all-strata lift, and complete costs.

## Disproof track

For exact all-occurrence B^2 buckets, audit every target-dependent branch bit and backpointer read; disprove the mechanism if any correct selector requires Query2P1, source incidence, or Omega(B^3) pair-by-fifth traffic.

## Positive and negative controls

- Positive: supplied duplicate-preserving labelled B^2 pair keys with long unary prefixes and exact all-occurrence replay.
- Negative: shuffled occurrence lists, omitted duplicate backpointers, empty/singleton restrictions, and blind targets whose only compatible fifth point forces a target-dependent selector.
- Baselines: explicit dictionaries, FM/FKS/KMP, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

Promote only with an endpoint-only exact restricted operation that derives target-dependent extendibility bits from B^2 state, replays every occurrence in the chosen bucket, proves sub-B^3 total traffic without Query2P1, reaches rank d_FB over at least max(d_FB+32,1,000) verified rows, completes 100 fresh blind descents, meets both caps, and has lambda,mu<=0.45. Falsify on a Query2P1/source-incidence selector, incomplete occurrence replay, Omega(B^3) traffic, false membership, cap failure, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-d/h01_selector_traffic_audit.md
- ideas/rejected/preallocation/artifacts/20260720-d/h01_trie_controls.json
- ideas/rejected/preallocation/artifacts/20260720-d/h01_cost_analysis.md

## Interpretation boundary

This rejects the elliptic key compiler, not PATRICIA. A toy success remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-d/h01_selector_traffic_audit.md; do not create it under this retired pre-ID screen.
