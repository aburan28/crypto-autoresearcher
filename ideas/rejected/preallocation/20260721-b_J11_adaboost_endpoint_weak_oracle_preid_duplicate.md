# Pre-ID duplicate draft — AdaBoost endpoint weak-oracle amplification

## Status and claim labels

- Prospect: `20260721-b-J11`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: adaptive_ensemble / high-risk / high-risk pre-ID screen.
- State: merged_rejected_target_trained_examples_and_no_exact_margin.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: retired zero-run snapshot only.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; training accuracy, a margin, or a verified relation is not an ECDLP result.

## Falsifiable hypothesis

Train target-independent weak predictors for exact restricted source existence from public endpoint features, amplify them with AdaBoost to an exact zero-error oracle, and use charged self-reduction to recover sources, factor logs, and fresh scalars below rho and BSGS.

## Mechanism-new operation

The native operation adaptively reweights supplied labelled examples and combines weak hypotheses into a margin classifier. It counts only if labels are derived without solving source existence, the weak advantage is uniform over fresh restrictions, and the ensemble supplies exact negative answers plus occurrence replay rather than distributional classification.

## Assumptions

1. Endpoint-only features support a target-independent weak learner with advantage bounded away from zero.
2. Training labels and reweighting do not call `Query2P1`, enumerate sources, or leak target scalars.
3. A proved margin converts ensemble score to exact emptiness on every restriction.
4. Positive classifications lift to labelled signed occurrences on all strata.
5. Training and inference generalize to relation and fresh masked-target distributions with complete cost charged.

## Semantic fingerprint

`public_endpoint_unlabelled_features | AdaBoost_adaptive_reweighting_weak_learners | exact_margin_restricted_classifier | positive_score_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact fresh restrictions and source replay remain the gate.
2. `ideas/rejected/ECDLP-IDEA-045_algebraic_hard_bit_shift_decoder_hypothesis.md` — predicting a bit without an exact algebraic lift does not solve ECDLP.
3. `ideas/rejected/ECDLP-IDEA-141_unambiguous_rectangle_source_factorization_hypothesis.md` — weak distributional separations do not give uniform source return.
4. `ideas/rejected/ECDLP-IDEA-347_countsketch_heavy_endpoint_source_decoder_hypothesis.md` — heavy-feature recovery misses rare exact sources.
5. `ideas/rejected/preallocation/20260720-a_E03_ransac_source_consensus_preid_duplicate.md` — learned/selected consensus begins from labelled source examples.

## Closest primary literature

- Freund and Schapire, [A decision-theoretic generalization of on-line learning and an application to boosting](https://doi.org/10.1006/jcss.1997.1504), derives adaptive multiplicative reweighting and boosting for supplied labelled examples.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not provide cheap exact training labels or a weak endpoint classifier.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source proves an exact ECDLP margin, label-free training, or source lift; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, features, restriction distribution, weak-learner class, training split, charts, labels policy, and verifier.
2. Produce training data and weak hypotheses from public endpoints without source-oracle labels; retain every example, weight, round, and cost.
3. For known-log targets, demand exact restricted decisions, make at most `5 ceil(log_2 B)+O(1)` self-reductions, obtain a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, include false/missed/dependent cases, require rank `d_FB`, and solve factor logs.
5. Freeze the ensemble before evaluating `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge label generation, feature computation, every weak learner and boosting round, sample complexity, margin certification, errors/retries, source replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge `T_labels+sum_k(T_weak(k)+T_reweight(k))+T_margin` and model state in `a,a_m`; charge all weak evaluations, retries, exact fallbacks, and replay in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, including generalization failure and target shift. Require error `<=2^-80`, both resource caps, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Boosting amplifies a weak learner only relative to supplied labelled examples and a distribution. Exact source-existence labels are the missing predicate, so training is circular unless it uses enumerated sources. Small classification error is inadequate for rare singleton/empty restrictions and fresh adversarial targets. A positive class score contains no source occurrence, so replay restores a separate missing oracle.

## Proof track

Construct label-free weak hypotheses from endpoint algebra, prove a uniform exact margin and source witness decoder, and establish target-shift, rank, and complete cost bounds.

## Disproof track

Audit every label and feature, withhold fresh target families, oversample empty/singleton restrictions, and falsify on any circular label, distributional error, or missing witness lift.

## Positive and negative controls

- Positive: supplied labelled separable data with a known weak learner and source backpointers.
- Negative: random labels, rare positives, zero-margin collisions, target shift, duplicate features, empty restrictions, and fresh targets.
- Baselines: the best weak learner, RANSAC, CountSketch, hard-bit controls, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with label-free endpoint training, an a priori uniform exact margin, zero errors over exhaustive toy restrictions and four sizes, full rank, 100 fresh held-out descents, failure at most `2^-80`, both caps, and `lambda,mu<=0.45`. Falsify on source-derived labels, empirical-only accuracy, any false negative/positive, absent replay, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j11_label_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j11_boosting_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j11_cost_analysis.md`

## Interpretation boundary

This rejects exact endpoint-oracle amplification, not AdaBoost classification. Finite accuracy is toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record and its retired zero-run snapshot to an independent `review-xhigh` Red Team; do not execute the contract.
