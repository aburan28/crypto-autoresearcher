# Pre-ID duplicate draft — A-star heuristic source search

## Status and claim labels

- Prospect: 20260720-d-H05; no canonical ECDLP idea ID was allocated
- Class / risk / lane: admissible_best_first_search / conservative / conservative pre-ID screen
- State: merged_rejected_supplied_transition_graph_and_completion_heuristic
- Evidence: complete live ledger/corpus and checked primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; correctness, a relation, or native algorithm performance is not an ECDLP result.

## Falsifiable hypothesis

Use a public admissible heuristic on partial signed decompositions so A-star reaches an exact target source before exploring the tuple tree, then completes logs and blind descent below rho/BSGS.

## Mechanism-new operation

A-star expands minimum g+h on a supplied state graph. It counts only if endpoints generate transitions and an informative target-uniform heuristic without solving completion; explicit tuple-tree search or post-hoc distances are controls.

## Assumptions

1. States/transitions are endpoint-derived without source-tree enumeration.
2. The heuristic is admissible, consistent, target-uniform, and generically informative.
3. Open/closed sets preserve signed occurrence provenance under restrictions.
4. Bounded failure has exact absence semantics, not timeout semantics.
5. Generation, heuristic, reopenings, replay, rank, logs, descent, bits, and memory are charged.

## Semantic fingerprint

public_partial_source_state | Astar_admissible_best_first | exact_restricted_goal | goal_path_to_signed_occurrences | logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — live uncommitted P1553 R4 exact restricted common-factor frontier.
2. ideas/rejected/preallocation/20260719-d_D01_soft_heap_source_priority_router_preid_duplicate.md — ordering starts from supplied states.
3. ideas/rejected/preallocation/20260720-c_G07_fibonacci_heap_source_frontier_preid_duplicate.md — faster frontier operations do not create transitions.
4. ideas/rejected/preallocation/20260720-b_F10_alpha_beta_source_game_tree_preid_duplicate.md — pruning needs a supplied tree and bounds.
5. ideas/rejected/preallocation/20260720-b_F11_uct_monte_carlo_source_tree_preid_duplicate.md — adaptive search consumes a simulator and lacks exact negatives.

## Closest primary literature

- Hart, Nilsson, and Raphael, [A Formal Basis for the Heuristic Determination of Minimum Cost Paths](https://doi.org/10.1109/TSSC.1968.300136), assumes a supplied graph and heuristic.
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

Let T_setup,M_setup compile only target-independent state rules and the heuristic evaluator. For one target let X_R be expanded states, E_R generated transitions, and T_search=O(E_R+(X_R+E_R)log X_R+X_R C_h). Charge a=log_N(T_setup), a_m=log_N(M_setup), q=log_N(Q_R(T_search+C_lift)+T_replay), and q_m=log_N(X_R+E_R+M_lift). No target search step appears in both a and q.

For B=N^beta, beta=1/5, let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ambiguity/rebuild/error overhead, and ell,ell_m factor-log time/state:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/advice/state <=B^(9/4+o(1)), complete fresh work/workspace <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values require one-sided 95% upper bounds below empirical gates.

## Likely fatal obstruction

An informative admissible completion heuristic is the missing restricted oracle; a weak one expands the source tree and a strong source-trained one imports answers.

## Proof track

Prove endpoint-only transitions/heuristic, admissibility, generic pruning/exhaustion bounds, exact lift, and full costs.

## Disproof track

Force source-tree expansion, show same public state has different completion distance, or identify source advice.

## Positive and negative controls

- Positive: supplied graph with exact-distance heuristic and labelled goal.
- Negative: zero/inadmissible heuristics, duplicate states, no-goal/blind targets.
- Baselines: uniform-cost, priority controls, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

Promote only with an endpoint-only exact restricted operation, exact occurrence lift, rank d_FB over at least max(d_FB+32,1,000) verified rows, 100 fresh blind descents, both caps, and lambda,mu<=0.45. Falsify on source advice, inadmissibility, false exhaustion, source-tree expansion, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-d/h05_heuristic_admissibility_audit.md
- ideas/rejected/preallocation/artifacts/20260720-d/h05_search_controls.json
- ideas/rejected/preallocation/artifacts/20260720-d/h05_cost_analysis.md

## Interpretation boundary

This rejects the elliptic heuristic/state compiler, not A-star. A toy success remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-d/h05_heuristic_admissibility_audit.md; do not create it under this retired pre-ID screen.
