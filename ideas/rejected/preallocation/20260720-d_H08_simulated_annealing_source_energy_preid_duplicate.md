# Pre-ID duplicate draft — Simulated-annealing source energy

## Status and claim labels

- Prospect: 20260720-d-H08; no canonical ECDLP idea ID was allocated
- Class / risk / lane: temperature_scheduled_source_optimizer / high_risk / high-risk pre-ID screen
- State: scoped_rejected_supplied_energy_and_no_exact_global_optimum_certificate
- Evidence: complete live ledger/corpus and checked primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; correctness, a relation, or native algorithm performance is not an ECDLP result.

## Falsifiable hypothesis

Construct endpoint energy whose zeros are exactly relations and anneal local moves to labelled zeros, then complete logs and blind descent below rho/BSGS.

## Mechanism-new operation

Simulated annealing cools a chain on a supplied energy. It counts only if energy avoids embedding answers, barriers/schedule are proved, and zero states lift exactly; post-hoc residual energy is a heuristic control.

## Assumptions

1. Energy is cheap, target-uniform, endpoint-only, and zero iff relation.
2. Local barriers admit a proved sub-rho schedule.
3. Restrictions require no retraining.
4. Zeros preserve signed occurrences and point verification.
5. Moves, rejects, restarts, cooling, replay, rank, logs, descent, bits, and memory are charged.

## Semantic fingerprint

public_endpoint_energy | simulated_annealing_schedule | zero_energy_exact_relation | minimizer_to_signed_occurrences | logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — live uncommitted P1553 R4 exact restricted common-factor frontier.
2. ideas/rejected/preallocation/20260720-a_E03_ransac_source_consensus_preid_duplicate.md — randomized optimization needs measurements.
3. ideas/rejected/preallocation/20260720-b_F11_uct_monte_carlo_source_tree_preid_duplicate.md — stochastic search lacks exact negatives.
4. ideas/rejected/ECDLP-IDEA-395_karger_stein_random_contraction_source_router_hypothesis.md — randomized recovery needs a graph.
5. ideas/rejected/ECDLP-IDEA-342_polymer_cluster_expansion_source_self_reduction_hypothesis.md — statistical interactions are supplied.

## Closest primary literature

- Kirkpatrick, Gelatt, and Vecchi, [Optimization by Simulated Annealing](https://doi.org/10.1126/science.220.4598.671), applies a schedule to a supplied energy.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not this source compiler.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs the required elliptic endpoint-to-source operation; ECDLP novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, signed decks, exceptional charts, native state, restriction grammar, and independent point verifier.
2. Construct only the target-independent energy evaluator, local-move rules, and frozen cooling schedule from public endpoints within B^(9/4+o(1)); do not run a target anneal or invoke Query2P1 in setup.
3. For R=[kappa]P, execute the full frozen temperature schedule and charged restarts. A verified zero-energy full labelled tuple, not a separate existence oracle, is the source return; charge false-zero and miss probability, then verify sum_i epsilon_i A_i=[kappa]P before recording sum_i epsilon_i y(A_i)=kappa in unknown logs.
4. Let d_FB be the actual distinct factor-log dimension; retain failures/dependencies, collect at least max(d_FB+32,1,000) verified rows, require rank d_FB, and only then solve factor logs.
5. Reuse unchanged state for R=Q+[t]P, replay a tuple, compute x=sum_i epsilon_i log_P(A_i)-t mod N, and independently verify [x]P=Q.
6. Charge construction, restrictions, failed queries, replay, relation density, rank, log solve, descent, scalar verification, bit complexity, and peak memory.

## Full rho/BSGS cost model

Let T_energy,M_energy compile only the target-independent evaluator, moves, and schedule. For one target use K temperatures, S_j steps at cost C_j, success probability p_R, and lift C_lift. Set a=log_N(T_energy), a_m=log_N(M_energy), q=log_N(Q_R(sum_j S_j C_j+C_lift)+T_replay), q_m=log_N(M_chain+M_lift). Charge log_N(1/p_R) once through delta or delta_t; adaptive restarts/misses enter u.

For B=N^beta, beta=1/5, let delta,delta_t be reciprocal verified-hit densities, r independent-rank credit, o output, u ambiguity/rebuild/error overhead, and ell,ell_m factor-log time/state:

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/advice/state <=B^(9/4+o(1)), complete fresh work/workspace <=N^(0.25+o(1))=B^(5/4+o(1)), and lambda,mu<=0.45. Rho expected time and BSGS time/memory are 0.50. Four increasing B values require one-sided 95% upper bounds below empirical gates.

## Likely fatal obstruction

Useful gradients toward a rare relation soften the missing oracle; generic residuals have unproved barriers, and annealing gives no exact absence.

## Proof track

Prove energy biconditional, barrier/schedule bounds under restrictions, exact lift, and full costs.

## Disproof track

Find false zero, super-cap barrier, source-dependent feature, or blind miss beyond the bound.

## Positive and negative controls

- Positive: planted energy with labelled zeros/known barriers.
- Negative: deceptive funnels, false zeros, shuffled labels, no-zero/blind targets.
- Baselines: local/random restart, UCT/RANSAC, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

Promote only with an endpoint-only exact restricted operation, exact occurrence lift, a proved cooling/barrier bound and total adaptive miss probability <=2^-80, rank d_FB over at least max(d_FB+32,1,000) verified rows, 100 fresh blind descents, both caps, and lambda,mu<=0.45. Falsify on source-bearing energy, false zero, barrier overflow, miss probability above 2^-80, cap failure, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-d/h08_energy_biconditional_audit.md
- ideas/rejected/preallocation/artifacts/20260720-d/h08_annealing_controls.json
- ideas/rejected/preallocation/artifacts/20260720-d/h08_cost_analysis.md

## Interpretation boundary

This rejects the elliptic energy/schedule, not simulated annealing. A toy success remains heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-d/h08_energy_biconditional_audit.md; do not create it under this retired pre-ID screen.
