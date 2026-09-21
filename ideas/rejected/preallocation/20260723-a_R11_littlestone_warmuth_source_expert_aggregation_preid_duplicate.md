# Pre-ID duplicate draft — Littlestone–Warmuth source-expert aggregation

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R11`; no canonical ID allocated.
- Disposition: `merged_rejected_supplied_experts_and_approximate_mistake_bound`.
- Class/risk: algorithm / high-risk.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; low mistake rate, a valid relation, or a validator pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, a target-independent pool of scalar-blind endpoint experts contains
one exact restricted-source predictor. Weighted-majority updates identify it quickly enough to
answer all restrictions, replay signed occurrences, complete factor logs, and solve 100 fresh
blind targets with exponents at most `0.45`.

## Mechanism-new operation

Weighted Majority combines predictions from a supplied expert pool and downweights experts after
mistakes. It counts only if experts and feedback are public-endpoint-derived without source
labels, and the aggregate becomes exact on every restriction with charged source replay.
Reweighting post-hoc predictors trained on known relations is a selector control.

## Assumptions

1. The fixed expert pool is built without source incidence, scalar labels, or hidden solvers.
2. Feedback revealing mistakes is available on relation and blind targets without knowing sources.
3. Mistake bounds strengthen to zero exact errors over every adaptive restriction.
4. The selected prediction has a charged inverse to signs, repetitions, and occurrence identities.
5. Training ends before and remains independent of the 100 blind targets.

## Semantic fingerprint

`public_endpoint_expert_pool | multiplicative_mistake_weight_updates | exact_restricted_source_predictor | charged_occurrence_self_reduction | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-b_J11_adaboost_endpoint_weak_oracle_preid_duplicate.md` — boosting cannot convert approximate weak predictors into exact empty-fibre semantics.
2. `ideas/rejected/preallocation/20260722-d_Q04_angluin_lstar_endpoint_learner_preid_duplicate.md` — exact teachers already implement Query2P1 and counterexample search.
3. `ideas/rejected/preallocation/20260720-a_E03_ransac_source_consensus_preid_duplicate.md` — post-hoc selection over supplied source-bearing samples is a control.
4. `ideas/rejected/preallocation/20260722-a_N11_walksat_noisy_source_local_search_preid_duplicate.md` — heuristic successes do not certify all-negative restrictions.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restricted decision and signed replay remain missing.

## Closest primary literature

- Littlestone and Warmuth, [The Weighted Majority Algorithm](https://doi.org/10.1006/INCO.1994.1009), proves mistake bounds for a supplied expert pool with revealed outcomes.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies equations but not source-blind experts or feedback.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

The exact expert and label-free feedback are outside the learning result; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, expert pool, initial weights, penalty, feedback, restrictions, adaptive schedule, strata, and verifier.
2. Build all target-independent experts and state within `B^(9/4+o(1))`; forbid source labels, accepted-relation training, scalar residues, and hidden decomposition.
3. For known-log targets, obtain exact restricted decisions, self-reduce to signed points, and verify each elliptic sum.
4. Collect at least `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and all factor logs.
5. Freeze weights and reuse identical state on 100 fresh masked targets, recover sources, subtract masks, and verify scalars.
6. Charge expert construction/evaluation, feedback acquisition, mistakes, adaptive restrictions, replay, failures, rank, logs, bits, and peak memory.

## Full rho/BSGS cost model

With `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal densities
`N^delta,N^delta_t`; expert/feedback query work `N^q,N^q_m`; rank credit `N^r`;
output `N^o`; ambiguity/mistakes `N^u`; and factor-log costs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho and BSGS remain exponent `0.50`.

## Likely fatal obstruction

Weighted Majority assumes labelled feedback and only competes with the best supplied expert; it
does not create that expert or guarantee zero errors. Exact feedback on an unknown restriction is
the missing predicate, and one false negative invalidates source self-reduction.

## Proof track

Prove a finite endpoint-only expert pool containing a perfect predictor, label-free exact
feedback, zero-error adaptive restriction behavior, subcap costs, and signed replay through blind
descent.

## Disproof track

Expose one source-labelled expert/feedback event, an unavoidable mistake, adaptive overfitting,
missed empty/rare fibre, replay ambiguity, or complete exponent `>=0.50`.

## Positive and negative controls

- Positive: supplied toy experts including one perfect source predictor with honest feedback.
- Negative: remove the perfect expert; add indistinguishable endpoints with different sources,
  adversarial labels, rare/empty fibres, post-hoc weight selection, and blind targets.
- Baselines: AdaBoost, L-star, RANSAC, P1553 R4, rho, and BSGS.
- Low regret or mistake count is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with zero errors over all four-size/all-strata adaptive restrictions, a source-
  blind perfect-expert theorem, full rank/logs, 100 blind descents, both caps, and
  `lambda,mu<=0.45`.
- Falsify on one source-labelled feedback bit, one exact error, cap violation, replay failure,
  or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r11_expert_feedback_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r11_adversarial_mistake_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r11_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Weighted Majority. Low regret, correct predictions, and valid
relations remain toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Remove source-labelled feedback from one toy expert protocol and preserve the first restriction on which all remaining endpoint-only experts agree incorrectly or prove zero-error replay.
