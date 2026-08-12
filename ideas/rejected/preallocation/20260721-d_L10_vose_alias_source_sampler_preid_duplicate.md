# Pre-ID duplicate draft — Vose alias source sampler

## Status and claim labels

- Prospect: `20260721-d-L10`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: randomized_algorithm / high-risk / high-risk pre-ID screen.
- State: merged_rejected_supplied_exact_distribution_and_sampling_not_emptiness.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a sampled relation or correct frequency is not an ECDLP result.

## Falsifiable hypothesis

Derive an exact endpoint-conditioned distribution on signed relation sources, preprocess it with Vose alias tables, sample useful independent relation tuples and fresh target decompositions in constant online time, and beat rho/BSGS after full setup, rank, logs, and descent costs.

## Mechanism-new operation

The native operation partitions a supplied finite distribution into equal-probability columns, each with a primary outcome, alias, and threshold, so sampling uses one uniform column and one comparison. It counts only if the exact distribution and occurrence labels are endpoint-derived below source scale and sampling supports zero-safe restrictions; aliasing a supplied source distribution is a control.

## Assumptions

1. Exact nonnegative source probabilities are computable from endpoints without enumerating sources or completion counts.
2. Alias table size and construction stay below setup/state caps.
3. Every nonempty restriction retains useful probability bounded away from source-density scale, while empty restrictions are certified exactly.
4. Samples replay occurrence-distinct signed tuples without cancellation or scalar labels.
5. The same target-independent sampler supports relation collection and fresh scalar-blind descent.

## Semantic fingerprint

`public_endpoint_exact_source_distribution | Vose_alias_table_partition | zero_safe_restricted_sampling | sampled_index_to_signed_occurrences | rank_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact all-negative predicate and signed occurrence replay frontier.
2. `ideas/rejected/preallocation/20260720-a_E12_reservoir_source_sampler_preid_duplicate.md` — streaming sampling begins after the source stream exists and cannot certify empty restrictions.
3. `ideas/rejected/preallocation/20260721-c_K06_jerrum_sinclair_canonical_path_source_sampler_preid_duplicate.md` — Markov sampling needs represented source states and useful stationary mass.
4. `ideas/rejected/preallocation/20260720-d_H07_metropolis_hastings_source_chain_preid_duplicate.md` — acceptance ratios and proposals assume the source distribution/state graph.
5. `ideas/rejected/preallocation/20260720-d_H09_gibbs_conditional_source_sampler_preid_duplicate.md` — exact conditionals are the missing completion counts and do not provide zero-safe replay.

## Closest primary literature

- Vose, [A linear algorithm for generating random numbers with a given distribution](https://doi.org/10.1109/32.92917), constructs constant-time samples after linear preprocessing of a supplied finite distribution.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives endpoint equations without an exact efficiently sampled source distribution.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), gives the generic baseline.

No checked source constructs exact endpoint probabilities, zero-safe restricted aliases, or the occurrence lift; the ECDLP transplant is novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, restrictions, exceptional strata, probability semantics, RNG, and independent point verifier.
2. Construct and certify endpoint-derived exact probabilities, alias columns, thresholds, and occurrence labels without source enumeration, completion-count oracles, or scalar advice.
3. For each known-log target, sample under at most `5 ceil(log_2 B)+O(1)` restrictions, replay `A_i,epsilon_i`, and verify `sum epsilon_i A_i=R` before retaining the row.
4. With actual `d_FB`, retain every failure/dependency, collect at least `max(d_FB+32,1000)` verified rows, require rank `d_FB`, and solve all factor logs.
5. Reuse unchanged state for `R=Q+[t]P`, sample/replay a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q` for 100 fresh targets.
6. Charge probability and table construction, exact arithmetic, rejection/restriction rebuilding, sample count, replay, density, rank, logs, descent, bit time, randomness, and memory.

## Full rho/BSGS cost model

Charge distribution/alias setup in `a,a_m`, restricted sampling/replay in `q,q_m`, and emitted/ambiguous samples in `o,u`. With `B=N^beta`, `beta=1/5`, density `delta,delta_t`, rank credit `r`, and log costs `ell,ell_m`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho and BSGS are `0.50`.

## Likely fatal obstruction

Vose accelerates draws only after an explicit exact probability vector is built. For relation fibres, computing those probabilities or restricted conditionals is the source-counting problem, and the alias arrays have one entry per outcome. Sampling cannot certify an empty restriction; rare useful relations still need inverse-density trials, while occurrence labels restore the source catalogue.

## Proof track

Construct exact endpoint-derived probabilities with a compact restriction-stable alias representation, prove nonnegligible useful mass and exact empty certification, and bound complete campaign/descent costs below the gates.

## Disproof track

Trace every probability and alias entry, compare useful-mass decay and zero queries, and falsify on completion-count/source advice, source-sized tables, false emptiness, or total exponent at least `0.50`.

## Positive and negative controls

- Positive: supplied finite distributions with planted labelled high-mass relation outcomes.
- Negative: empty restrictions, singleton mass `B^-5`, duplicate/canceling outcomes, exact-rounding edge cases, and fresh targets.
- Baselines: direct categorical sampling, reservoir, Metropolis-Hastings, Gibbs, Jerrum-Sinclair, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only after endpoint-only exact distribution construction, four increasing sizes, zero false empty decisions, exact replay, full rank from at least `max(d_FB+32,1000)` rows, 100 fresh blind descents, both caps, and one-sided 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied probability vectors, source-scale aliases, useful mass forcing exponent `>=0.50`, or one false decision.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-d/l10_probability_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-d/l10_alias_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-d/l10_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint-only alias-sampling transplant, not Vose sampling from supplied distributions. Every finite sample remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not execute an experiment.
