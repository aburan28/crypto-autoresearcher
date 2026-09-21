# Pre-ID duplicate draft — Merkle source commitment tree

## Status and claim labels

- Prospect: 20260720-a-E10; no canonical ECDLP idea ID was allocated
- Class / risk / lane: authenticated_tree_representation / representation-changing / representation-changing pre-ID screen
- State: merged_rejected_committed_source_leaves_and_no_root_inversion
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; authenticated membership or a valid proof path is not scalar recovery.

## Falsifiable hypothesis

Commit target-independent endpoint/source buckets as leaves of a Merkle tree. A public target label and source restriction would determine a root predicate whose accepting branch can be opened by logarithmic authentication paths, returning exact signed factor-base occurrences for relation collection and fresh blind descent below rho and BSGS.

## Mechanism-new operation

A Merkle tree recursively hashes supplied leaves so a short authentication path proves membership relative to a committed root. It counts only if leaves are constructed endpoint-only below the gate, the root enables exact restricted nonemptiness without a supplied opening, and an accepting proof reveals point-faithful sources. Committing an explicit relation/source catalogue is a control.

## Assumptions

1. Target-independent leaves cover all signed and exceptional source strata without tuple materialization.
2. Leaf construction, hashing, tree nodes, roots, restriction commitments, openings, absence proofs, replay, rank, logs, descent, bit time, and memory are charged.
3. The root or a public derived operation identifies an accepting branch without already knowing the witness.
4. Authentication paths preserve source ancestry and support arbitrary restrictions without rebuilding the committed tree.
5. One frozen commitment serves known-log and fresh scalar-blind targets without trapdoors, scalar labels, or external provers holding the source catalogue.

## Semantic fingerprint

public_endpoint_leaf_commitments | Merkle_hash_tree | exact_restricted_root_nonemptiness | authentication_path_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires endpoint-derived exact restricted nonemptiness and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public exact source-resolving circuit.
3. ideas/rejected/ECDLP-IDEA-339_gacs_korner_common_part_source_keys_hypothesis.md — compact common keys do not reconstruct exact source occurrences.
4. ideas/rejected/ECDLP-IDEA-374_fiat_naor_function_inversion_source_index_hypothesis.md — inversion advice over supplied mappings stores the missing source index.
5. ideas/rejected/ECDLP-IDEA-404_stone_duality_source_ultrafilter_hypothesis.md — compact Boolean/ultrafilter representation does not yield a point-faithful source section.

## Closest primary literature

- Merkle, [A digital signature based on a conventional encryption function](https://doi.org/10.1007/3-540-48184-2_32), authenticates supplied leaves/messages through a hash tree; it neither discovers an unknown member nor certifies arbitrary subset emptiness from the root.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) gives endpoint equations, not commitment openings.
- Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) gives the baseline.

No checked source supplies endpoint-only leaf generation, public root inversion, or complete descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, leaf encoding, hash function, tree shape, restriction commitments, opening grammar, and verifier.
2. Construct target-independent tree/root within B^(9/4+o(1)) without enumerating source tuples.
3. For known-log R=[kappa]P, derive exact restricted nonemptiness from public commitments, open one branch, replay labelled points A_i with signs epsilon_i using at most 5 ceil(log_2 B)+O(1) restriction queries plus failed siblings, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; preserve failed/negative proofs and dependencies, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse unchanged commitments for fresh R=Q+[t]P, open a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge leaf/tree construction, all hashes, proof providers or search, absence proofs, restriction roots, openings, rank, logs, descent, scalar checks, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge leaf creation, all tree nodes/roots, restriction commitments, and opening satellites; q,q_m charge target predicate compilation, branch search, every absence/membership proof, restrictions, bisection, and replay. Let delta,delta_t be reciprocal verified accepting-opening densities, r independent-rank credit, o output, u hash collisions/opening ambiguity/prover search, and ell,ell_m factor-log time/state.

Let L be leaf count, Q_R restriction queries, C_hash one hash, C_search root-only discovery work, and C_open verification work. Building and storing an ordinary tree cost Theta(L C_hash) and Theta(L) hashes; verifying a supplied authentication path is O(log L) hashes, but root-only unknown-member discovery is Omega(L) absent a separately charged index or source-holding prover. Set a=log_N(T_leaves+L C_hash), a_m=log_N(L+M_satellite), q=log_N(Q_R(C_search+C_open)+T_replay), and q_m=log_N(M_search+M_open). Restriction-specific trees multiply construction/state. Collision/preimage assumptions authenticate supplied leaves; they neither locate a leaf nor prove arbitrary subset emptiness.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh search/restriction/opening <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho and BSGS baselines are 0.50. All leaves, any external prover/catalogue, nonmembership structure, and branch search are charged; logarithmic verification is not logarithmic discovery.
The complete fresh masked-target discovery/opening/replay path must independently be <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion needs four increasing B values with one-sided 95% upper bounds on L, build/state, root-only search, restriction, fresh, and complete exponents and exact empty/singleton controls.

## Likely fatal obstruction

A Merkle root commits supplied leaves but is intentionally noninvertible. Constructing source-labelled leaves materializes the missing catalogue; authentication paths verify a witness already known to a prover and do not discover one. Ordinary Merkle trees also lack exact arbitrary-subset nonmembership, and restriction-specific roots require rebuilding or a complete labelled tree. This merges with IDEAS 120/339/374/404.

## Proof track

Give endpoint-only sub-gate leaves and a public root operation that returns exact restricted existence plus an opening without a source-holding prover, then close replay and descent costs.

## Disproof track

Show any opening/search requires a source catalogue/prover, or give two leaf sets with indistinguishable admitted public commitment interface but different restricted accepting support.

## Positive and negative controls

- Positive: a supplied leaf and authentication path must verify against the frozen root.
- Negative: root-only unknown-member discovery, empty/singleton restricted subtrees, equal endpoint leaves with different ancestry, absent/exceptional targets, restrictions, and blind targets.
- Baselines: IDEAS 120/339/374/404, explicit authenticated dictionaries, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only leaves, public exact restricted discovery/opening without a source prover, all-strata replay, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-labelled materialized leaf, one required source-holding prover, one unsupported nonmembership restriction, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e10_leaf_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e10_root_discovery_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e10_cost_analysis.md

## Interpretation boundary

This rejects the proposed discovery use, not Merkle authentication. Correct membership verification or a short proof path is not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-a/e10_leaf_provenance.md; do not create it under the retired snapshot.
