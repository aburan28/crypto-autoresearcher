# Pre-ID duplicate draft — Auer UCB source-arm selector

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R12`; no canonical ID allocated.
- Disposition: `merged_rejected_reward_oracle_posthoc_selector`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; low regret, a selected arm, a valid relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, endpoint-defined source partitions are bandit arms whose
scalar-blind rewards reveal exact restricted-source density. Upper-confidence selection locates
nonempty arms, supports exact signed self-reduction, completes factor logs, and solves 100 fresh
blind targets with complete time and memory exponents at most `0.45`.

## Mechanism-new operation

UCB balances exploration and exploitation by selecting the arm with the largest empirical mean
plus confidence radius. It counts only if rewards are public, scalar-blind, exact enough to
certify zero versus rare nonzero support, and the selected arm replays occurrences. Choosing
among source partitions using success labels is a post-hoc selector control.

## Assumptions

1. Arms are target-independent public partitions with no stored source membership.
2. Reward samples are generated without solving the restricted source problem or using scalars.
3. Confidence bounds certify exact zeros and rare positive arms after all adaptive restrictions.
4. Selected arms support charged recovery of signs, repetitions, and occurrence identities.
5. The learned policy is frozen before 100 fresh blind targets and satisfies both caps.

## Semantic fingerprint

`public_endpoint_source_partition_arms | upper_confidence_exploration_exploitation | exact_nonempty_arm_decision | charged_signed_occurrence_replay | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-a_E09_bootstrap_particle_source_filter_preid_duplicate.md` — adaptive sampling begins from a supplied transition/reward model.
2. `ideas/rejected/preallocation/20260721-b_J11_adaboost_endpoint_weak_oracle_preid_duplicate.md` — adaptive weighting cannot create exact source labels.
3. `ideas/rejected/preallocation/20260720-a_E03_ransac_source_consensus_preid_duplicate.md` — success-driven selection over supplied samples is post hoc.
4. `ideas/rejected/preallocation/20260721-b_J10_hnsw_source_proximity_router_preid_duplicate.md` — adaptive routing assumes a source-bearing index and lacks exact negatives.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted existence and signed replay remain the owner.

## Closest primary literature

- Auer, Cesa-Bianchi, and Fischer, [Finite-Time Analysis of the Multiarmed Bandit Problem](https://doi.org/10.1023/A:1013689704352), analyzes exploration from supplied stochastic reward observations.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not provide the claimed source-density reward oracle.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls generic costs.

Bandit selection does not supply the reward oracle or exact source inverse; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, arm family, reward generator, confidence schedule, tie rule, restrictions, strata, seeds, and verifier.
2. Build target-independent arms/state inside `B^(9/4+o(1))`, forbidding source membership tables, scalar labels, and decomposition calls.
3. For known-log targets, sample rewards, certify a nonempty restricted arm, self-reduce to signed points, and verify the elliptic sum.
4. Obtain at least `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and every factor log.
5. Freeze policy/state for 100 fresh masked targets, recover sources, subtract masks, and verify every scalar.
6. Charge arm construction, every pull, reward generation, confidence failures, adaptive restrictions, replay, rank, logs, bit operations, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal densities
`N^delta,N^delta_t`; arm/reward query work `N^q,N^q_m`; rank credit `N^r`; output
`N^o`; ambiguity/regret/failure repetitions `N^u`; and factor-log costs
`N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain `0.50`.

## Likely fatal obstruction

A reward that distinguishes a rare nonempty restriction from an empty one is Query2P1 in
statistical form. UCB permits regret and wrong pulls, whereas exact self-reduction permits no
false negatives. Observed successes are post-hoc source labels and do not transfer to blind
targets without paying the original density.

## Proof track

Prove a source-blind exact reward oracle, zero-error confidence for arbitrarily rare arms,
subcap adaptive sample complexity, and signed source replay through full logs and blind descent.

## Disproof track

Expose one source-labelled reward, rare arm below confidence resolution, adaptive selection
leakage, one false empty decision, replay ambiguity, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied Bernoulli toy arms with one planted labelled nonempty source arm.
- Negative: zero and `1/M` reward gaps, swapped arm identities, empty fibres, adversarial
  nonstationarity, post-hoc seed selection, exceptional strata, and blind targets.
- Baselines: particle filtering, AdaBoost, RANSAC, P1553 R4, rho, and BSGS.
- Low regret or correct arm selection is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero errors over four sizes/all strata and all adaptive restrictions,
  source-blind exact rewards, full rank/logs, 100 blind descents, both caps, and
  `lambda,mu<=0.45`.
- Falsify on one source-labelled reward, one missed rare arm, cap violation, replay failure,
  or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r12_reward_oracle_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r12_rare_arm_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r12_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not UCB. Low regret, selected arms, and valid relations remain toy,
heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Replace success-labelled rewards with public endpoint-only observations in one toy arm family and preserve the first indistinguishable empty/rare pair or prove exact subcap separation.
