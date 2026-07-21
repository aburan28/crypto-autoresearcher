# Pre-ID duplicate draft — RANSAC source consensus

## Status and claim labels

- Prospect: 20260720-a-E03; no canonical ECDLP idea ID was allocated
- Class / risk / lane: randomized_consensus_search / high-risk / high-risk pre-ID screen
- State: merged_rejected_supplied_measurements_and_density_amplification
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: no executable contract
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; fitting a planted consensus model is not an ECDLP break.

## Falsifiable hypothesis

Treat public partial-sum endpoint records as measurements, sample minimal subsets, fit an elliptic compatibility model, and score consensus on held-out records. If true relation sources form a detectable inlier population, RANSAC could return exact signed tuples at sufficient density for factor logs and fresh blind descent below rho and BSGS.

## Mechanism-new operation

RANSAC repeatedly draws minimal samples, fits a model, and selects it by consensus under an outlier-heavy measurement distribution. It counts only if measurements are endpoint-derived without source enumeration, inlier testing is not the missing relation predicate, and the sampling success plus consensus scan are charged. Sampling explicit partial tuples or scoring with a completion oracle is a control.

## Assumptions

1. Relation-bearing endpoints form a target-uniform inlier population of density high enough for sub-rho minimal-subset sampling.
2. Measurement construction, samples, model fitting, consensus scans, false models, restrictions, replay, rank, logs, descent, verification, randomness, bit time, and memory are charged.
3. Inlier scoring is exact on every signed/exceptional chart and returns source ancestry.
4. The fitted model generalizes from known-log relations to fresh scalar-blind targets without target leakage.
5. No post-hoc threshold, explicit tuple pool, large-prime table, dense resultant, or source oracle is admitted.

## Semantic fingerprint

public_endpoint_measurements | RANSAC_minimal_subset_model_fit | exact_consensus_inlier_test | consensus_record_to_signed_source | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 freezes exact restricted target-label existence.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the absent public source-resolving circuit.
3. inputs/ledger_inventory_20260719.json — ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY charges labelled source records.
4. ideas/rejected/ECDLP-IDEA-079_zero_free_partition_conditioning_hypothesis.md — conditioning does not create rare exact sources.
5. ideas/rejected/ECDLP-IDEA-134_preprocessed_three_sum_source_oracle_hypothesis.md — preprocessed completion/scoring assumes the source oracle.

## Closest primary literature

- Fischler and Bolles, [Random Sample Consensus](https://doi.org/10.1145/358669.358692), fits models from supplied measurements under a probabilistic inlier assumption; it does not construct rare relation measurements.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives an endpoint condition but no high-density consensus population.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), gives the baseline.

No checked source supplies target-uniform ECDLP inlier density, exact source replay, or a complete descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, measurement map, minimal-sample size, fit rule, consensus threshold, restrictions, random seeds, and verifier.
2. Construct target-independent measurements within B^(9/4+o(1)) without enumerating partial tuples.
3. For known-log R=[kappa]P, sample and fit until an exact restricted accepting model appears; replay labelled points A_i with signs epsilon_i using charged bisection, verify sum_i epsilon_i A_i=[kappa]P, and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; record failed models/dependencies, collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse frozen state/rules for fresh R=Q+[t]P; recover a tuple, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge measurement generation, reciprocal all-inlier sample probability, every fit and consensus scan, restrictions, replay, rank, logs, descent, scalar verification, bit operations, and memory.

Replay permits at most 5 ceil(log_2 B)+O(1) restriction queries plus all failed branches and singleton checks.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge measurement construction and fit/consensus state; q,q_m charge target-conditioned fitting, complete consensus scans, restrictions, bisection, and replay. Let delta,delta_t charge only the outer density of relation/target instances that actually possess a valid source in the frozen measurement population, excluding the internal all-inlier sampling event; J below charges that event solely in q. Let r be independent-rank credit, o output, u false models/threshold ambiguity not already included in J, and ell,ell_m factor-log time/state.

Let M be the measurement count, w the exact inlier fraction, s the minimal sample size, eta the allowed failure probability, C_fit one fit, and C_score one measurement score. The required trials are J=ceil(log(eta)/log(1-w^s)); native work is at least J(C_fit+Theta(M C_score)) and state includes all M measurements or their charged generator. Set a=log_N(T_measure), a_m=log_N(M_measure_state), q=log_N(J(C_fit+M C_score)+T_restriction+T_replay), and q_m=log_N(M_live+M_model). If w=B^(-zeta) and s is fixed, the sampling term alone is B^(s zeta+o(1)); the inlier predicate and model dimension must be constructed and charged rather than assumed.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh work <=B^(5/4+o(1)), and lambda,mu<=0.45. Pollard rho expected time and BSGS time/memory are 0.50. If an s-point minimal fit needs inlier fraction w, the w^(-s) sampling factor and every O(number of measurements) consensus scan are included in delta+q.
Separately require the full fresh masked-target J-fit/score/replay work <=N^(0.25+o(1))=B^(5/4+o(1)). Four increasing B values must give a one-sided 95% upper bound below each exponent gate and a lower confidence bound on w sufficient for the frozen J formula.

## Likely fatal obstruction

RANSAC exploits a supplied measurement set and an available inlier predicate. Here the measurement records or exact consensus test already encode the missing source compatibility. Generic relation density is rare, so all-inlier sampling restores brute-force source search; endpoint-only coarse measurements create false consensus without source ancestry. This merges with IDEAS 079/134/137 and sampling controls rather than removing P1553 R4.

## Proof track

Prove an endpoint-only measurement construction, a target-uniform lower bound on exact inlier density, a source-faithful consensus inverse, and the complete rank/descent costs.

## Disproof track

Identify one source-bearing measurement or inlier test, construct equal endpoint consensus scores with different source validity, or show w^(-s) times consensus scans reaches exponent 0.50.

## Positive and negative controls

- Positive: a supplied high-inlier synthetic measurement set with planted exact source-labelled model.
- Negative: same marginal endpoint distribution with shuffled source labels, vanishing inlier density, false-consensus models, absent targets, exceptional charts, restrictions, and blind targets.
- Baselines: IDEAS 079/134/137, uniform explicit tuple sampling, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only measurements, proved target-uniform inlier density, exact all-strata replay, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source measurement/oracle, one consensus/source mismatch, fitted target leakage, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e03_measurement_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e03_consensus_shuffle_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e03_cost_analysis.md

## Interpretation boundary

This rejects the ECDLP transplant, not RANSAC. Toy model recovery, robust fitting, or one valid relation is not a breakthrough.

## Exactly one next executable action

1. Write ideas/rejected/preallocation/artifacts/20260720-a/e03_measurement_provenance.md and classify the minimal sample, fit rule, and every consensus test by whether it consumes source-bearing state.
