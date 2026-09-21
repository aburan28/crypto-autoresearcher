# Pre-ID duplicate draft — Bootstrap particle source filter

## Status and claim labels

- Prospect: 20260720-a-E09; no canonical ECDLP idea ID was allocated
- Class / risk / lane: sequential_monte_carlo / high-risk / high-risk pre-ID screen
- State: merged_rejected_supplied_transition_model_and_particle_degeneracy
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; posterior tracking or a planted trajectory is not scalar recovery.

## Falsifiable hypothesis

Model signed source selection as a hidden-state process and public partial sums as observations. A bootstrap particle filter would propagate, weight, and resample partial source trajectories so that posterior mass concentrates on exact target decompositions, producing relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

The bootstrap filter represents a recursive Bayesian posterior by sampled particles propagated through a supplied transition model, weighted by a supplied likelihood, and resampled. It counts only if transition/likelihood evaluation is endpoint-derived without source enumeration, rare valid trajectories retain enough mass under every restriction, and a particle returns exact signed sources. Filtering an explicit source simulator is a control.

## Assumptions

1. There is a target-uniform hidden-state model whose transition and observation likelihoods are public and source-faithful.
2. Particle initialization, propagation, likelihoods, normalization, resampling, genealogies, restrictions, failures, replay, rank, logs, descent, randomness, bit time, and memory are charged.
3. Exact accepting trajectories have provably nonnegligible posterior mass and avoid path degeneracy.
4. Resampled ancestry returns five point-faithful occurrences and exact absence is certified without infinite particles.
5. One frozen model/proposal serves known-log and fresh scalar-blind targets without learned target leakage or an explicit source simulator.

## Semantic fingerprint

public_hidden_source_process | bootstrap_particle_propagate_weight_resample | exact_restricted_posterior_support | particle_genealogy_to_signed_occurrence | factor_logs_and_blind_descent

## Five closest ledger entries

1. ledger/FINDING-PF-IC-001.md — ECFG-P1553-ZR-R4 requires exact restricted support and replay.
2. inputs/ledger_inventory_20260719.json — ECFG-H675 identifies the missing public source-resolving circuit.
3. inputs/ledger_inventory_20260719.json — ECFG-H676 bars generators whose leaves materialize source fibres.
4. ideas/rejected/ECDLP-IDEA-316_doob_h_transform_endpoint_source_bridge_hypothesis.md — a target-conditioned transition bridge assumes the missing harmonic/source information.
5. ideas/rejected/ECDLP-IDEA-367_amp_onsager_source_reconstruction_hypothesis.md — approximate iterative reconstruction needs a supplied source model and exactification.

## Closest primary literature

- Gordon, Salmond, and Smith, [Novel approach to nonlinear/non-Gaussian Bayesian state estimation](https://doi.org/10.1049/ip-f-2.1993.0015), propagates samples through a supplied state-transition and measurement model; it does not construct elliptic source dynamics.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) gives endpoint equations, not a high-mass posterior over source paths.
- Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) gives the baseline.

No checked source supplies the transition/likelihood compiler, zero-error support, or complete descent; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, signed decks, charts, state space, transition/proposal, likelihood, particle count, resampling seeds, restrictions, and verifier.
2. Build target-independent model/state within B^(9/4+o(1)) without enumerating source paths.
3. For known-log R=[kappa]P, filter under every charged restriction until a verified genealogy yields labelled points A_i with signs epsilon_i; verify sum_i epsilon_i A_i=[kappa]P and record sum_i epsilon_i y(A_i)=kappa (mod N) in unknown factor logs y(A).
4. Use at most 5 ceil(log_2 B)+O(1) restriction queries plus all failed siblings for replay. Let d_FB be the number of distinct factor-log unknowns after cross-deck identifications and normalization; collect at least max(d_FB+32,1,000) verified equations, require rank d_FB, and only then solve.
5. Reuse the frozen model for fresh R=Q+[t]P, recover a genealogy, compute x=sum_i epsilon_i log_P(A_i)-t (mod N), and verify [x]P=Q.
6. Charge all particles, likelihoods, normalizations, resampling draws, discarded genealogies, restrictions, zero-event certification, rank, logs, descent, verification, bit operations, and peak memory.

## Full rho/BSGS cost model

For B=N^beta, beta=1/5, let a,a_m charge model construction and particle/genealogy state; q,q_m charge target observations, all propagation/weight/resampling steps, restrictions, bisection, and replay. Let delta,delta_t charge only outer relation/target availability before particle sampling, excluding the accepting-path proposal mass p and K-particle miss event charged below in q. Let r be independent-rank credit, o output, u effective-sample-size loss/path degeneracy not already included in K, and ell,ell_m factor-log time/state.

Let K be particle count, T stages, p the exact accepting-path mass under the frozen proposal/posterior, eta the allowed miss probability, and C_step one propagate/weight/resample step. Native time is Theta(K T C_step) and full genealogy state is Theta(KT) unless recomputed. The miss probability is (1-p)^K, so K>=log(eta)/log(1-p), asymptotically Omega(log(1/eta)/p); if p=B^(-zeta), K=B^(zeta+o(1)). Set a=log_N(T_model), a_m=log_N(M_model), q=log_N(Q_R K T C_step+T_replay), and q_m=log_N(KT+M_model). No finite K certifies zero support, which remains a separate exactness obstruction.

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require state <=B^(9/4+o(1)), fresh filtering/restriction/replay <=B^(5/4+o(1)), and lambda,mu<=0.45. Rho and BSGS baselines are 0.50. Particle count sufficient for simultaneous rare-event coverage, full genealogies, likelihood precision, and exact absence amplification are charged.
Every fresh masked-target filter/genealogy/replay path must independently fit <=N^(0.25+o(1))=B^(5/4+o(1)). Promotion needs four increasing B values with one-sided 95% upper bounds on eta,p,K, model/build/state/fresh/complete exponents, and exact zero-support controls rather than an empirical miss.

## Likely fatal obstruction

The bootstrap filter assumes a transition simulator and likelihood; exact versions are the missing source generator and Query2P1. Generic valid decompositions are rare, so resampling collapses onto high-weight aggregate endpoints and loses the unique valid genealogy. Finite particles cannot certify empty support, while retaining all paths is source enumeration. This merges with IDEAS 316/321/367/401.

## Proof track

Construct endpoint-only transitions and likelihoods, prove a target-uniform posterior mass/anti-degeneracy bound plus exact support and genealogy inversion, then close full descent costs.

## Disproof track

Expose one source-bearing transition/likelihood or build two hidden-source models with identical observable particle weights but different accepting support; alternatively show required particle count reaches exponent 0.50.

## Positive and negative controls

- Positive: a supplied state-space model with a high-mass planted source trajectory and exact genealogy.
- Negative: a rare unique trajectory lost during resampling, identical observations with different hidden ancestry, zero-support instances, exceptional charts, restrictions, and blind targets.
- Baselines: IDEAS 316/321/367/401, direct sequential source sampling, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only model construction, zero-error restricted support, proved anti-degeneracy, exact all-strata genealogies, at least max(d_FB+32,1,000) verified equations of rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one supplied source transition/likelihood, one lost accepting genealogy or false absence, particle/state cap violation, target-trained proposal, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-a/e09_model_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-a/e09_particle_degeneracy_controls.json
- ideas/rejected/preallocation/artifacts/20260720-a/e09_cost_analysis.md

## Interpretation boundary

This rejects the transplant, not particle filtering. Toy posterior concentration or one valid trajectory is not an ECDLP breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-a/e09_model_provenance.md; do not create it under the retired snapshot.
