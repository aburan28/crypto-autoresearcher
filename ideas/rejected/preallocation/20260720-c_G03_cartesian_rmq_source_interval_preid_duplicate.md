# Pre-ID duplicate draft — Cartesian-tree RMQ source interval

## Status and claim labels

- Prospect: 20260720-c-G03; no canonical ECDLP idea ID was allocated
- Class / risk / lane: cartesian_tree_range_minimum / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_source_array_and_posthoc_minimum_score
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: finite controls are toy; score extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; constant-time RMQ on a supplied array is not an ECDLP result.

## Falsifiable hypothesis

Place partial source candidates in a public array whose interval minima identify exact accepting completions. A Cartesian tree with static RMQ preprocessing would answer canonical restriction queries, replay signed occurrences, collect full-rank relations, and descend fresh blind targets below rho and BSGS.

## Mechanism-new operation

A Cartesian tree is simultaneously heap-ordered by supplied array values and in-order by array positions; after linear-space LCA/RMQ preprocessing it supports static range minima. It counts only if the array order and scores are endpoint-derived without enumerating candidates, minima are exactly source-valid, and restrictions are canonical intervals. Building RMQ over explicit source scores is a control.

## Assumptions

1. Public endpoints induce a target-independent array order and exact all-strata score.
2. Array construction, stack/tree build, LCA/RMQ state, queries, restrictions, ties, replay, rank, logs, descent, bit time, and memory are charged.
3. Every queried minimum is biconditional with an accepting signed source and preserves its occurrence label.
4. The source restrictions needed for five-coordinate bisection map to O(1) array intervals without rebuilding.
5. Fresh blind targets reuse the same scores/state without post-hoc ordering.

## Semantic fingerprint

public_source_score_array | Cartesian_tree_static_RMQ | exact_restricted_accepting_minimum | RMQ_position_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted source frontier.
2. ideas/rejected/preallocation/20260719-d_D03_suffix_array_source_interval_index_preid_duplicate.md — interval indexes require a supplied source text/order.
3. ideas/rejected/preallocation/20260719-c_C01_elias_fano_monotone_endpoint_dictionary_preid_duplicate.md — monotone positions do not construct source-bearing keys.
4. ideas/rejected/preallocation/20260720-b_F12_fusion_tree_endpoint_predecessor_preid_duplicate.md — fast predecessor begins after exact ordered endpoints exist.
5. ideas/rejected/ECDLP-IDEA-143_monge_transport_source_section_hypothesis.md — a score/order that selects a true source is the missing section.

## Closest primary literature

- Gabow, Bentley, and Tarjan, [Scaling and related techniques for geometry problems](https://doi.org/10.1145/800057.808675), develops and uses the Cartesian-tree maximum/minimum structure for a supplied array; it is not claimed here as the first Cartesian-tree source.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but no source-ordering score.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic array, exact minimum/source theorem, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, array order, score, tie rule, RMQ convention, restriction map, and verifier.
2. Construct the array oracle, Cartesian tree, and LCA/RMQ state within B^(9/4+o(1)) without source enumeration.
3. For R=[kappa]P, use exact interval minima to replay A_i,epsilon_i under at most 5 ceil(log_2 B)+O(1) restrictions plus failed siblings; verify the point sum, then record the unknown-log row.
4. Collect at least max(d_FB+32,1,000) verified rows, retain misses/dependencies, require rank d_FB, and solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, recover a tuple, compute x, and verify [x]P=Q.
6. Charge array generation, every score/tie, tree/RMQ build, interval decomposition, queries, replay, rank, logs, blind descent, bit time, and state.

## Full rho/BSGS cost model

Let n be array length, C_score score work, M_score score state, I_R the total intervals across restrictions, and C_inv replay. A supplied Cartesian tree builds in O(n), and linear-space static RMQ preprocessing/query costs are O(n) and O(1) respectively in the word model. Set a=log_N(T_array+n C_score+T_RMQ), a_m=log_N(M_score+n), q=log_N(I_R C_RMQ+Q_R C_inv+T_replay), q_m=log_N(M_RMQ+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

RMQ reports minima only after a source-bearing array and valid score are supplied. Coarse endpoint scores cannot distinguish compatible occurrences; exact scores answer Query2P1 pointwise or materialize the catalogue. Five independent source restrictions are not generally contiguous intervals. This merges with D03/C01/F12/IDEA-143.

## Proof track

Prove endpoint-only array/score construction, restriction-to-interval theorem, exact all-strata minimum/source biconditional, rank, and blind descent under the caps.

## Disproof track

Find one canonical source restriction whose members are noncontiguous in every public order, or two same-score positions with different validity.

## Positive and negative controls

- Positive: a supplied array with unique planted labelled minima and interval restrictions.
- Negative: shuffled positions, tied incompatible minima, noncontiguous restrictions, empty/singleton intervals, exceptional and blind targets.
- Baselines: D03/C01/F12, IDEA-143, direct score scan, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with compact endpoint-only array/score, O(1)-interval restrictions, exact source replay, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source score, noncontiguous restriction beyond cap, false minimum, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g03_interval_order_audit.md
- ideas/rejected/preallocation/artifacts/20260720-c/g03_rmq_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g03_cost_analysis.md

## Interpretation boundary

This rejects the proposed elliptic RMQ array, not Cartesian trees. Correct RMQ answers or a planted relation are not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g03_interval_order_audit.md; do not create it under the retired snapshot.
