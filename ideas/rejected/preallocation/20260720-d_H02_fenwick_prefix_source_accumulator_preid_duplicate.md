# Pre-ID duplicate draft — Fenwick prefix source accumulator

## Status and claim labels

- Prospect: 20260720-d-H02; no canonical ECDLP idea ID was allocated
- Class / risk / lane: hierarchical_prefix_accumulator / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_source_array_and_noninvertible_prefix_sums
- Evidence: complete live ledger/corpus and checked primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; correctness, a relation, or native algorithm performance is not an ECDLP result.

## Falsifiable hypothesis

Order public endpoint cells and store exact extendibility indicators in a Fenwick tree; prefix differences and bisection would recover a signed source, complete logs, and descend fresh blind targets below rho/BSGS.

## Mechanism-new operation

A Fenwick tree maintains prefix sums of a supplied array. It counts only if exact indicator cells are endpoint-derived without Query2P1/source enumeration and restrictions are bounded interval unions; a post-hoc answer array is a control.

## Assumptions

1. A public target-uniform order makes every restriction a bounded interval union.
2. Exact cells are built without source enumeration.
3. Updates, prefix queries, replay, rank, logs, descent, bit time, and state are charged.
4. A positive singleton lifts to exact occurrences.
5. The structure is unchanged for fresh blind targets.

## Semantic fingerprint

public_ordered_endpoint_cells | Fenwick_lowbit_prefix_accumulation | exact_interval_counts | singleton_to_signed_occurrences | logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — live uncommitted P1553 R4 exact restricted common-factor frontier.
2. ideas/rejected/preallocation/20260719-b_B01_wavelet_tree_rank_select_source_router_preid_duplicate.md — rank/select starts from a source sequence.
3. ideas/rejected/preallocation/20260719-c_C01_elias_fano_monotone_endpoint_dictionary_preid_duplicate.md — monotone encoding consumes ordered keys.
4. ideas/rejected/preallocation/20260719-d_D02_count_min_source_frequency_sketch_preid_duplicate.md — summaries lose exact rare identity.
5. ideas/rejected/preallocation/20260720-c_G03_cartesian_rmq_source_interval_preid_duplicate.md — interval queries need a source array.

## Closest primary literature

- Fenwick, [A New Data Structure for Cumulative Frequency Tables](https://doi.org/10.1002/spe.4380240306), maintains prefix frequencies for a supplied table.
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

For n cells charge T_cell+O(n) build and O(log n) per prefix/update: a=log_N(T_cell+n), a_m=log_N(M_cell+n), q=log_N(Q_R(log n+C_inv)+T_replay), q_m=log_N(M_tree+M_inv).

For B=N^beta, beta=1/5, let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ambiguity/rebuild/error overhead, and ell,ell_m factor-log time/state:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/advice/state <=B^(9/4+o(1)), complete fresh work/workspace <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values require one-sided 95% upper bounds below empirical gates.

## Likely fatal obstruction

The exact cell array is componentwise r_R: constructing it is the missing Query2P1 operation, while independent source restrictions need not be contiguous.

## Proof track

Prove endpoint-only cells, bounded-interval restrictions, exact singleton lift, and complete costs.

## Disproof track

Show one cell requires enumeration, one restriction fragments, or one positive prefix cannot identify an occurrence.

## Positive and negative controls

- Positive: supplied sparse labelled 0/1 array.
- Negative: fragmented restrictions, collisions, shuffled labels, no-hit/blind targets.
- Baselines: explicit arrays, wavelet/Elias-Fano/RMQ, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

Promote only with an endpoint-only exact restricted operation, exact occurrence lift, rank d_FB over at least max(d_FB+32,1,000) verified rows, 100 fresh blind descents, both caps, and lambda,mu<=0.45. Falsify on source-bearing cell, fragmented rebuild, false count, cap failure, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-d/h02_cell_construction_audit.md
- ideas/rejected/preallocation/artifacts/20260720-d/h02_prefix_controls.json
- ideas/rejected/preallocation/artifacts/20260720-d/h02_cost_analysis.md

## Interpretation boundary

This rejects the endpoint indicator array, not Fenwick prefix sums. A toy success remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-d/h02_cell_construction_audit.md; do not create it under this retired pre-ID screen.

