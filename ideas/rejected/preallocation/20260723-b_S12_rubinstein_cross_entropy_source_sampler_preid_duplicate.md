# Pre-ID duplicate draft — Rubinstein cross-entropy source sampler

## Status and claim labels

- Provisional ID: `PREID-20260723-b-S12`; no canonical ID allocated.
- Disposition: `merged_rejected_posthoc_elite_selector_and_parametric_proposal`.
- Class/risk/lane: algorithm / high-risk / high-risk pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; objective improvement, elite concentration, or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-only score and parametric proposal family permit cross-entropy updates from elite
signed-source samples to concentrate on exact elliptic relations without source leakage. The
resulting proposal would supply full-rank relations and 100 blind descents with complete time and
memory exponents at most `0.45`.

## Mechanism-new operation

The cross-entropy method samples from a supplied parametric family, selects elite samples under a
supplied score, and updates parameters toward the elite distribution. It counts only if endpoints
provide source-free sampling and scoring, elite selection is predeclared and scalar-blind, and
accepted samples replay exact signed occurrences. Post-hoc selection from enumerated sources is a
control.

## Assumptions

1. Proposal sampling avoids explicit source products and has inverse-polynomial relation coverage.
2. The public score is exact enough to separate valid fibres without encoding the missing predicate.
3. Elite fraction, updates, smoothing, restarts, rare-event variance, and failures satisfy caps.
4. Proposal parameters preserve signs, multiplicities, source identity, and exceptional strata.
5. Frozen family/update rules generalize to fresh masks without target- or success-conditioned tuning.

## Semantic fingerprint

`public_endpoint_parametric_source_proposal | score_ranked_elite_cross_entropy_update | concentrated_exact_relation_sampling | elite_state_to_signed_occurrences | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — proposal adaptation still requires public density/score semantics and hit bounds.
2. `ideas/rejected/preallocation/20260722-a_N11_walksat_noisy_source_local_search_preid_duplicate.md` — score-driven local search on a supplied landscape does not construct the exact relation predicate.
3. `ideas/rejected/preallocation/20260723-a_R12_auer_ucb_source_arm_selector_preid_duplicate.md` — adaptive post-hoc selection cannot create the missing exact reward/source oracle.
4. `ideas/rejected/ECDLP-IDEA-367_amp_onsager_source_reconstruction_hypothesis.md` — iterative distribution updates assume a tractable generative observation model.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable existence and occurrence replay remain the required gate.

## Closest primary literature

- Rubinstein, [The Cross-Entropy Method for Combinatorial and Continuous Optimization](https://doi.org/10.1023/A:1010091220143), adaptively updates a supplied parametric sampling distribution using elite objective values.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations but no source-free proposal, exact score, or replay.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic comparison.

No checked source supplies the ECDLP proposal/score compiler, nonleaking update theorem,
occurrence inverse, or complete descent. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, proposal family, initialization, score, elite fraction, update/smoothing, restrictions, lift, strata, masks, seeds, stopping rules, and verifier.
2. Compile target-independent proposal/score state within `B^(9/4+o(1))`, forbidding source tables, target-trained selectors, scalar logs, dense resultants, and Query2P1.
3. For known-log targets, charge every sample, score, sort/selection, update, rejected generation, restart, and lift; verify signed point sums before rows.
4. Retain failures/dependencies, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve every factor log.
5. Reuse byte-identical eligible state on 100 fresh `Q+[t]P`, sample/replay elite relation states, subtract masks, and independently verify all scalars.
6. Charge construction, proposal state, generation, scoring, elite storage, adaptation, density, replay, rank, logs, bit work, and peak memory.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`; reciprocal verified densities
`N^delta,N^delta_t`; sampling/scoring/update/lift work and workspace `N^q,N^q_m`;
rank credit `N^r`; output `N^o`; adaptation/failure amplification `N^u`; and
factor-log costs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, with `0<=r<=o`. Require
`lambda,mu<=0.45`, setup/state `<=B^(9/4+o(1))`, and fresh work/workspace
`<=B^(5/4+o(1))`. Rho expected time and BSGS time/memory remain `0.50`.

## Likely fatal obstruction

Cross-entropy updates amplify whatever the score already detects. An exact score separating valid
relations is the missing predicate; a proxy can concentrate on near-relations or a post-hoc
artifact with no exact hit-density gain. Proposal samples are still source candidates, so
generation cost and elite occurrence storage restore the brute-force/source-catalogue budget.

## Proof track

Prove endpoint-only proposal generation and exact scoring, predeclared nonleaking updates,
inverse-polynomial relation coverage, all-strata replay, full rank/logs, blind descent, and
complete sub-rho costs.

## Disproof track

Expose source enumeration or label leakage, an equal-score valid/invalid pair, elite collapse on
near-relations, target-conditioned tuning, overfit selector behavior, or complete exponent at
least `0.50`.

## Positive and negative controls

- Positive: a supplied rare-event toy model with a score biconditional to labelled valid states.
- Negative: equal-score valid/invalid pairs, near-relation attractors, elite collapse, shuffled labels, empty fibres, exceptional strata, and blind targets.
- Baselines: Metropolis-Hastings, WalkSAT, UCB/post-hoc selectors, AMP, P1553 R4, rho, and BSGS.
- Objective improvement or elite concentration is only toy/model-bound evidence.

## Quantitative promotion and falsification gates

- Promote only with public proposal/score/replay theorems, zero semantic errors at four sizes/all strata, total miss probability at most `2^-80`, full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one source-bearing proposal/score, post-hoc selector, false elite, cap breach, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-b/s12_proposal_score_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260723-b/s12_elite_collapse_cases.json`
- `ideas/rejected/preallocation/artifacts/20260723-b/s12_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the specified ECDLP transplant, not the cross-entropy method. Objective improvement,
elite concentration, or a valid row remains `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Construct a toy valid/invalid signed-source pair with identical frozen public score and audit whether any source-free cross-entropy update separates the pair before seeing relation labels.
