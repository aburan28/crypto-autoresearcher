# Pre-ID duplicate draft — Gale–Shapley source matching

## Status and claim labels

- Prospect: 20260720-c-G09; no canonical ECDLP idea ID was allocated
- Class / risk / lane: deferred_acceptance_matching / conservative / general pre-ID screen
- State: merged_rejected_supplied_preference_lists_and_pairwise_not_fiveway_feasibility
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: finite controls are toy; preference transplants are heuristic, model-bound, and novelty-unverified
- Breakthrough claim: none; a stable matching on supplied preferences is not an ECDLP relation collector.

## Falsifiable hypothesis

Construct public preference lists between complementary partial-source states so stable proposals converge to compatible partners. Deferred acceptance would select exact signed source tuples under restrictions, support full-rank relations, and descend fresh blind targets below rho and BSGS.

## Mechanism-new operation

Gale–Shapley iterates proposals and rejections on supplied preference lists to find a stable matching. It counts only if preferences are endpoint-derived without testing source compatibility, stability is biconditional with five-way elliptic feasibility, and matched agents replay occurrences. Replacing one matching solver on an explicit compatibility graph is a control.

## Assumptions

1. Public target-independent preference lists cover every signed and exceptional source stratum.
2. List construction, proposals, rejections, ties, restrictions, verification, replay, rank, logs, descent, bit time, and memory are charged.
3. Stable pairs are exact five-source witnesses rather than pairwise-compatible fragments.
4. Restrictions update lists without source-sized recomputation and preserve provenance.
5. Fresh blind targets do not alter preferences using scalar or post-hoc source information.

## Semantic fingerprint

public_partial_source_preferences | Gale_Shapley_deferred_acceptance | exact_restricted_stable_source_match | matched_agents_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted five-source frontier.
2. ideas/rejected/preallocation/20260720-b_F06_hungarian_primal_dual_source_assignment_preid_duplicate.md — assignment costs consume an explicit compatibility matrix.
3. ideas/rejected/preallocation/20260719-b_B04_edmonds_blossom_source_matching_preid_duplicate.md — pair matching does not certify five-way source feasibility.
4. ideas/rejected/ECDLP-IDEA-382_gallai_edmonds_source_matching_decomposition_hypothesis.md — matching decompositions begin from a supplied graph.
5. ideas/rejected/ECDLP-IDEA-392_irving_leather_rotation_poset_source_matching_hypothesis.md — stable-matching rotations preserve supplied preference information.

## Closest primary literature

- Gale and Shapley, [College admissions and the stability of marriage](https://doi.org/10.1080/00029890.1962.11989827), proves stability for supplied preferences, not elliptic source existence.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), supplies endpoint constraints but no source-free preference compiler.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source gives a stability/source biconditional or complete descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, agent sets, preferences/tie policy, restriction updates, match-to-source map, and verifier.
2. Construct target-independent preferences within B^(9/4+o(1)) without enumerating compatible pairs/tuples.
3. For known-log R, run restricted deferred acceptance, replay A_i,epsilon_i, verify point equality, and record the unknown-log row.
4. Collect at least max(d_FB+32,1,000) verified rows, retain unstable/false matches and dependencies, require rank d_FB, and solve logs.
5. Reuse unchanged preference state for Q+[t]P, recover a tuple, compute x, and verify [x]P=Q.
6. Charge list construction, every proposal/rejection/tie, restrictions, tuple verification, replay, density, rank, logs, blind descent, bit time, and state.

## Full rho/BSGS cost model

Let L be total preference-list length, P_prop proposals, Q_R restrictions, C_pref preference construction/comparison work, C_exact tuple verification, and C_inv replay. Deferred acceptance makes O(L) proposals on supplied strict lists. Set a=log_N(T_agents+L C_pref), a_m=log_N(M_lists), q=log_N(Q_R(P_prop C_pref+C_exact+C_inv)+T_replay), and q_m=log_N(M_lists+M_match+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds. Rho/BSGS are 0.50.

## Likely fatal obstruction

Preferences that rank true partners encode the missing compatibility predicate. Pairwise stability does not imply a five-way elliptic sum, and a stable matching can exist when no target relation exists. Exact lists materialize edges; coarse lists give false matches. This merges with F06/B04/IDEAS 382/392.

## Proof track

Prove endpoint-only preferences, an exact all-strata stability/source biconditional under restrictions, provenance, rank, and blind descent.

## Disproof track

Give a stable matching assembled from pairwise-compatible fragments with no valid five-source tuple, or expose one source-bearing preference comparison.

## Positive and negative controls

- Positive: supplied strict preferences with a planted labelled stable match.
- Negative: stable-but-invalid pairings, ties, shuffled source labels, empty/singleton restrictions, exceptional and blind targets.
- Baselines: F06/B04/IDEAS 382/392, explicit matching, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only preferences, exact source biconditional/replay, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-bearing preference, stable false positive, missing source under restrictions, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g09_preference_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g09_stability_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g09_cost_analysis.md

## Interpretation boundary

This rejects the elliptic preference transplant, not deferred acceptance. Stability or one verified match is not a breakthrough.

## Exactly one next executable action

1. Submit this record for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g09_preference_provenance.md; do not create it under this retired pre-ID screen.
