# Pre-ID duplicate draft — Hopcroft DFA source partition

## Status and claim labels

- Prospect: 20260720-c-G01; no canonical ECDLP idea ID was allocated
- Class / risk / lane: automaton_partition_refinement / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_transition_table_and_acceptance_partition
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; minimizing a supplied automaton is not an ECDLP result.

## Falsifiable hypothesis

Compile partial signed factor-base assignments into a deterministic automaton whose accepting language is exactly the target relation language. Hopcroft partition refinement would quotient equivalent prefixes, support exact restricted acceptance and source replay, collect full-rank factor-base relations, and descend fresh blind targets below rho and BSGS.

## Mechanism-new operation

Hopcroft repeatedly splits DFA state blocks by inverse transitions to compute the coarsest right-invariant partition refining accepting versus rejecting states. It counts only if the transition table and initial accepting split are derived from public elliptic endpoints without enumerating source prefixes or calling Query2P1, and if quotient states retain an exact occurrence lift. Minimizing an explicitly compiled source automaton is a control.

## Assumptions

1. A target-uniform finite alphabet and public transition table recognize every signed and exceptional source stratum exactly.
2. State generation, inverse transitions, accepting labels, refinement, restrictions, replay, rank, logs, descent, bit time, and state are charged.
3. Every positive quotient state has a point-faithful lift to signed factor-base occurrences.
4. Canonical source restrictions update the automaton without rebuilding a source-sized table.
5. The same minimized machine serves known-log and fresh scalar-blind targets.

## Semantic fingerprint

public_partial_relation_DFA | Hopcroft_inverse_transition_partition_refinement | exact_restricted_acceptance | quotient_state_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted common-factor frontier.
2. ideas/rejected/ECDLP-IDEA-377_courcelle_mso_tree_automaton_source_compiler_hypothesis.md — an automaton is useful only after the source structure is compiled.
3. ideas/rejected/ECDLP-IDEA-394_weisfeiler_leman_tuple_refinement_source_quotient_hypothesis.md — stable refinement loses source distinctions unless neighbours are supplied.
4. ideas/rejected/ECDLP-IDEA-383_modular_decomposition_source_quotient_hypothesis.md — quotient blocks consume an explicit compatibility graph.
5. ideas/rejected/preallocation/20260719-c_C08_equality_saturation_source_egraph_preid_duplicate.md — congruence closure starts from supplied terms and rewrite edges.

## Closest primary literature

- Hopcroft, [An n log n algorithm for minimizing states in a finite automaton](https://i.stanford.edu/TR/CS-TR-71-190.html), assumes a supplied DFA transition table and accepting set.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a compact deterministic source automaton.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required elliptic DFA, restriction updates, or occurrence lift; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, charts, alphabet, state equivalence, transition/acceptance rules, restriction grammar, and verifier.
2. Construct the target-independent DFA and inverse-transition lists within B^(9/4+o(1)) without enumerating source prefixes.
3. For R=[kappa]P, use exact restricted acceptance to replay labelled A_i and signs epsilon_i in at most 5 ceil(log_2 B)+O(1) queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P, then record sum_i epsilon_i y(A_i)=kappa in unknown logs.
4. Let d_FB be the actual distinct factor-log dimension; retain failures and dependencies, collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, replay a tuple, compute x=sum_i epsilon_i log_P(A_i)-t mod N, and verify [x]P=Q.
6. Charge compilation, all transition/refinement traffic, restrictions, lifts, relation density, rank, logs, descent, verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let s be the number of reachable DFA states, k the alphabet size, e<=ks the represented transitions, Q_R the restriction queries, and C_inv the occurrence lift. Hopcroft costs O(e log s) time and O(e+s) state on its supplied DFA. Set a=log_N(T_compile+e log s), a_m=log_N(M_compile+e+s), q=log_N(Q_R(C_accept+C_inv)+T_replay), and q_m=log_N(M_machine+M_inv). Let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ambiguity/rebuild/state-splitting overhead, and ell,ell_m factor-log time/state.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work/workspace <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values need one-sided 95% upper bounds below every gate.

## Likely fatal obstruction

The DFA transition table and accepting split are the missing relation compiler. Endpoint-only coarse states merge prefixes with different completions; source-faithful states reproduce the B^5 prefix tree or Query2P1 transition oracle. Hopcroft removes behaviourally redundant supplied states but creates no new acceptance information. This merges with IDEAS 377/383/394.

## Proof track

Prove a compact endpoint-derived DFA, exact all-strata language equivalence under every restriction, point-faithful quotient lift, and the complete bounds.

## Disproof track

Exhibit two source prefixes with the same public endpoint state but different accepting continuations, or one transition/acceptance bit that requires source enumeration.

## Positive and negative controls

- Positive: a supplied minimalizable DFA with planted labelled accepting words.
- Negative: shuffled occurrence labels, Myhill-Nerode-distinct prefix collisions, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEAS 377/383/394, explicit prefix automata, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only compilation, exact restriction-stable acceptance/lift, rank d_FB over at least max(d_FB+32,1,000) rows, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing transition, false acceptance, quotient-lift collision, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g01_state_collision_audit.md
- ideas/rejected/preallocation/artifacts/20260720-c/g01_acceptance_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g01_cost_analysis.md

## Interpretation boundary

This rejects the proposed elliptic DFA compiler, not Hopcroft minimization. A smaller automaton, valid word, or relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g01_state_collision_audit.md; do not create it under this retired pre-ID screen.
