# Pre-ID duplicate draft — UCT Monte Carlo source tree

## Status and claim labels

- Prospect: 20260720-b-F11; no canonical ECDLP idea ID was allocated
- Class / risk / lane: bandit_guided_tree_search / high-risk / high-risk pre-ID screen
- State: merged_rejected_supplied_transition_simulator_and_no_exact_absence
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; a high-reward rollout or planted trajectory is not scalar recovery.

## Falsifiable hypothesis

Treat partial source assignments as tree states and use UCT upper-confidence selection to focus rollouts on branches likely to reach an exact target. A verified terminal trajectory would yield relations, and a reusable tree would descend fresh blind targets below rho and BSGS.

## Mechanism-new operation

UCT applies a multi-armed-bandit confidence score to choose children, expands a supplied transition model, simulates rollouts, and backs up rewards. It counts only if state transitions and rewards are endpoint-derived without source/completion oracles, sampling finds rare exact terminals within the gate, and restrictions have zero-error absence semantics. Post-hoc reward shaping is a control.

## Assumptions

1. A target-independent transition simulator covers all signed and exceptional source strata exactly.
2. State/action generation, rewards, rollouts, confidence terms, tree storage, restrictions, replay, rank, logs, descent, randomness, time, and memory are charged.
3. A verified terminal trajectory has sufficient density, while negative branches receive exact certificates rather than finite-sample absence.
4. Tree aggregation preserves occurrence genealogy under arbitrary restrictions.
5. The same state serves fresh blind targets without target-trained rewards or scalar hints.

## Semantic fingerprint

public_partial_source_MDP | UCT_confidence_rollout_backup | exact_restricted_terminal_search | rollout_genealogy_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted existence and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source resolver.
3. ideas/rejected/ECDLP-IDEA-079_zero_free_partition_conditioning_hypothesis.md — exact search-to-decision needs the missing predicate.
4. ideas/rejected/preallocation/20260720-a_E03_ransac_source_consensus_preid_duplicate.md — randomized trials consume source measurements and rare-hit probability.
5. ideas/rejected/preallocation/20260720-a_E09_bootstrap_particle_source_filter_preid_duplicate.md — sampled trajectories cannot certify zero support and need a supplied model.

## Closest primary literature

- Kocsis and Szepesvári, [Bandit based Monte-Carlo planning](https://doi.org/10.1007/11871842_29), introduces UCT for supplied finite-horizon or discounted MDPs; it does not construct an elliptic transition simulator or exact absence oracle.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives endpoint equations, not bandit actions or rewards.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the model, rare-source guarantee, exact negatives, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, state/action/reward model, UCT constant, rollout/seed rules, restrictions, and verifier.
2. Build target-independent simulator/tree state within B^(9/4+o(1)) without source-tree enumeration.
3. For R=[kappa]P, obtain a verified terminal trajectory and replay labelled A_i,epsilon_i in at most 5 ceil(log_2 B)+O(1) restriction queries plus failed siblings; verify sum_i epsilon_i A_i=[kappa]P, then record sum_i epsilon_i y(A_i)=kappa.
4. Collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, retain every failed/censored rollout and dependency, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, recover a trajectory, compute x=sum_i epsilon_i log_P(A_i)-t, and verify [x]P=Q.
6. Charge all model construction, actions, simulations, rewards, backups, restrictions, negative certification, genealogy, replay, rank, logs, descent, seeds, checks, bit time, and memory.

## Full rho/BSGS cost model

Let K be rollouts, horizon d, V_K stored tree nodes, C_step transition/reward work, Q_R restrictions, and C_inv genealogy inversion. Let H_(j-1) be the history before rollout j and p_(R,j)(H_(j-1)) its conditional verified-terminal probability. For adaptive UCT,

P_miss(R,K)=E[product_(j=1)^K (1-p_(R,j)(H_(j-1)))].

The simplification (1-p_R)^K is allowed only for independently sampled rollouts from a genuinely frozen policy. Define s_R(K)=1-P_miss(R,K) for the complete adaptive query. Keep K inside q=log_N(Q_R(Kd C_step+C_inv+T_negative)+T_replay), set a=log_N(T_model), a_m=log_N(M_model), and q_m=log_N(M_model+V_K+Kd_genealogy+M_inv). With beta=1/5, let delta and delta_t be the reciprocal relation-target and blind-target success exponents of the complete K-rollout queries; do not charge a per-rollout rarity exponent again. The remaining r,o,u,ell,ell_m terms retain their common meanings:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), complete fresh work <=N^(0.25+o(1))=B^(5/4+o(1)), lambda,mu<=0.45, and four increasing-B one-sided 95% bounds on hit, time, and state exponents. Rho and BSGS are 0.50.

## Likely fatal obstruction

The transition simulator or reward is the missing source/completion oracle. Exact elliptic targets are generically rare; bandit concentration optimizes expected reward but does not turn finite rollouts into exact absence. Reward shaping can leak source labels, and merged tree states lose genealogy. This merges with IDEA-079 and pre-ID E03/E09.

## Proof track

Construct an endpoint-only simulator and prove a sub-gate accepting density plus zero-error restriction certificates, point-faithful genealogy, rank, and blind descent.

## Disproof track

Expose one source-bearing transition/reward, a unique terminal with nonnegligible adaptive P_miss(R,K), or two genealogies merged into the same public state.

## Positive and negative controls

- Positive: a supplied toy MDP with one planted high-reward labelled terminal path.
- Negative: unique rare terminals, reward-preserving shuffled ancestry, finite-rollout false absence, empty/singleton restrictions, exceptional and blind targets.
- Baselines: IDEA-079, pre-ID E03/E09, uniform tree search, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only model/reward, exact restriction negatives, bounded complete-query relation and blind-target success exponents delta and delta_t derived from s_R(K)=1-P_miss(R,K), rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source oracle, one finite-sample absence claim, genealogy collision, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-b/f11_model_reward_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-b/f11_rare_terminal_controls.json
- ideas/rejected/preallocation/artifacts/20260720-b/f11_cost_analysis.md

## Interpretation boundary

This rejects the elliptic UCT transplant, not Monte Carlo planning. A verified rollout, reward gain, or one relation is not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-b/f11_model_reward_provenance.md; do not create it under the retired snapshot.
