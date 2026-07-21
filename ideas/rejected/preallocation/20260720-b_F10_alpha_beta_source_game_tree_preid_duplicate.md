# Pre-ID duplicate draft — Alpha–beta source game tree

## Status and claim labels

- Prospect: 20260720-b-F10; no canonical ECDLP idea ID was allocated
- Class / risk / lane: adversarial_tree_pruning / high-risk / high-risk pre-ID screen
- State: merged_rejected_supplied_game_tree_evaluator_and_ordering
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; pruning a supplied game tree is not scalar recovery.

## Falsifiable hypothesis

Cast source selection and exclusion as alternating moves: the maximizer chooses factor occurrences and the minimizer challenges incompatible continuations. Exact alpha–beta bounds would prune subtrees, leaving a principal variation that replays a valid relation and blind descent below rho and BSGS.

## Mechanism-new operation

Alpha–beta search propagates exact minimax lower/upper bounds and prunes branches that cannot affect the root value of a supplied game tree. It counts only if legal moves and leaf values are endpoint-derived cheaply, the root value exactly decides restricted source existence, and the principal variation yields labelled factors. Post-hoc move ordering or a completion oracle is a control.

## Assumptions

1. A target-independent finite game covers all signed and exceptional source strata exactly.
2. Move generation, ordering, leaf evaluation, bounds, transpositions, restrictions, replay, rank, logs, descent, time, and memory are charged.
3. Minimax value is biconditional with source existence, and pruned siblings have sound exact absence certificates.
4. Principal variations preserve occurrence ancestry under arbitrary restrictions.
5. One game representation serves fresh blind targets without source-trained ordering.

## Semantic fingerprint

public_source_challenge_game | alpha_beta_exact_minimax_bounds | exact_restricted_root_value | principal_variation_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 is the exact restricted-decision residual.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source resolver.
3. ideas/rejected/ECDLP-IDEA-079_zero_free_partition_conditioning_hypothesis.md — exact self-reduction still needs a valid restriction predicate.
4. ideas/rejected/ECDLP-IDEA-343_avis_fukuda_reverse_search_source_enumerator_hypothesis.md — local child/parent operations encode the source graph.
5. ideas/rejected/preallocation/20260719-a_A10_cegar_endpoint_abstraction_source_refinement_preid_duplicate.md — refinement is only useful with a sound exact counterexample oracle.

## Closest primary literature

- Knuth and Moore, [An analysis of alpha-beta pruning](https://doi.org/10.1016/0004-3702(75)90019-3), analyzes pruning for supplied game trees and exact leaf values; it does not construct an elliptic source game.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint equations, not legal moves or minimax evaluations.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the game, leaf oracle, sound ordering, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, players, legal moves, leaf values, ordering/tie rules, restrictions, and verifier.
2. Build target-independent game state within B^(9/4+o(1)) without source-tree materialization.
3. For R=[kappa]P, solve exact restricted games, replay the principal variation as labelled A_i,epsilon_i in at most 5 ceil(log_2 B)+O(1) queries plus failed siblings, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, preserve pruned/failed branches, and only then solve factor logs.
5. Reuse unchanged game state for R=Q+[t]P, recover a variation, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge every generated move, leaf evaluation, bound update, ordering probe, transposition, restriction, absence certificate, replay, rank, logs, descent, check, bit operation, and memory cell.

## Full rho/BSGS cost model

Let branching b, depth d, V_AB visited nodes, C_move move-generation cost, C_leaf exact leaf cost, Q_R restrictions, and C_inv path inversion. Worst-case V_AB=Theta(b^d); ideal source-informed ordering can approach Theta(b^(d/2)) but its construction is charged. Set a=log_N(T_game), a_m=log_N(M_game), q=log_N(Q_R(V_AB(C_move+C_leaf)+C_inv)+T_replay), and q_m=log_N(M_game+d+M_trans+M_inv). With beta=1/5 and delta,delta_t,r,o,u,ell,ell_m:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds. Rho and BSGS are 0.50.

## Likely fatal obstruction

Legal-move and leaf evaluators are the missing source/completion predicate. Exact absence can force the full game tree; good move ordering is source-bearing post-hoc advice. Aggregate states can join incompatible prefixes, while faithful transpositions materialize source ancestry. This merges with IDEA-079/343 and pre-ID A10.

## Proof track

Construct an endpoint-only exact game with sound sub-gate pruning and principal-variation/source inversion stable under restrictions, then close costs.

## Disproof track

Expose one source-bearing move/leaf oracle, an adversarial ordering requiring b^d nodes, or a principal variation assembled from incompatible ancestry.

## Positive and negative controls

- Positive: a supplied toy game with exact leaf values and a unique planted principal variation.
- Negative: adversarial move order, equal bounds with different source validity, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEA-079/343, pre-ID A10, exhaustive source trees, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only moves/values, exact restricted root/source inversion, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source oracle, unsound prune, source-trained ordering, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f10_game_oracle_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f10_adversarial_order_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f10_cost_analysis.md

## Interpretation boundary

This rejects the elliptic game encoding, not alpha–beta pruning. A correct principal variation or one relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f10_game_oracle_provenance.md; do not create it under this retired pre-ID screen.
