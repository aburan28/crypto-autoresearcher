# Pre-ID duplicate draft — Rauch–Tung–Striebel source trajectory smoother

## Status and claim labels

- Prospect: 20260720-c-G12; no canonical ECDLP idea ID was allocated
- Class / risk / lane: forward_backward_linear_gaussian_smoothing / high-risk / high-risk pre-ID screen
- State: merged_rejected_supplied_linear_state_model_and_posterior_not_exact_source
- Evidence: complete live ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: retired zero-run text snapshot
- Labels: toy, heuristic, model-bound, novelty-unverified
- Breakthrough claim: none; reconstructing a toy Gaussian trajectory is not an ECDLP solve.

## Falsifiable hypothesis

Represent successive partial-source sums as a low-dimensional latent linear state with public noisy endpoint observations. A Kalman forward pass followed by Rauch–Tung–Striebel smoothing would reconstruct the most likely full signed source trajectory, yielding relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

RTS smoothing combines a supplied linear-Gaussian state model's forward filtered means/covariances with a backward gain recursion to estimate past states conditioned on all observations. It counts only if the finite-field elliptic model and noise law are derived without source trajectories, posterior concentration implies an exact source with quantified density, and rounding/replay is exact. Smoothing simulated source observations is a control.

## Assumptions

1. Public endpoint features obey a target-independent low-dimensional linear transition/observation model over a specified domain.
2. Model fitting, covariances, inversions, precision, forward/backward passes, restrictions, rounding, verification, replay, rank, logs, descent, time, and memory are charged.
3. The noise distribution is justified for actual elliptic source ensembles and does not encode the hidden trajectory.
4. Posterior states lift uniquely to signed occurrences under every restriction and exceptional chart.
5. Fresh blind targets use the frozen model without target/scalar retraining.

## Semantic fingerprint

public_partial_sum_state_space_model | RTS_forward_backward_covariance_smoothing | exact_restricted_trajectory_reconstruction | smoothed_state_to_signed_occurrences | factor_logs_and_blind_descent

## Five closest ledger entries

1. ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md — the uncommitted working-tree P1553 R4 exact restricted-source and replay frontier.
2. ideas/rejected/preallocation/20260720-a_E08_viterbi_source_trellis_preid_duplicate.md — dynamic programming requires a supplied state/emission model.
3. ideas/rejected/preallocation/20260720-a_E09_bootstrap_particle_source_filter_preid_duplicate.md — sampled filters cannot certify exact absence and consume a transition model.
4. ideas/rejected/ECDLP-IDEA-308_hermann_krener_nonlinear_source_observer_hypothesis.md — observability begins from a supplied source-sensitive output map.
5. ideas/rejected/ECDLP-IDEA-367_amp_onsager_source_reconstruction_hypothesis.md — probabilistic reconstruction needs a justified random sensing model and exact replay.

## Closest primary literature

- Rauch, Tung, and Striebel, [Maximum likelihood estimates of linear dynamic systems](https://doi.org/10.2514/3.3166), derives smoothing for a supplied linear dynamic/noise model.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), gives exact nonlinear endpoint equations, not a low-dimensional Gaussian state model.
- Shoup, [Generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), supplies the baseline.

No checked source supplies the elliptic state/noise model, exact trajectory lift, or descent; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, state/observation features, domain, transition/noise matrices, precision, smoothing/rounding rules, restrictions, and verifier.
2. Fit or derive the target-independent model within B^(9/4+o(1)) without observing hidden source trajectories outside declared toy controls.
3. For known-log R, run forward filtering/backward smoothing, round and replay A_i,epsilon_i under bounded restrictions, verify point equality, and record a row.
4. Collect at least max(d_FB+32,1,000) verified rows, preserve posterior failures/censoring/dependencies, require rank d_FB, and solve factor logs.
5. Reuse the frozen model for Q+[t]P, recover a trajectory, compute x, and verify [x]P=Q.
6. Charge model derivation/training data, all dense algebra and precision, restriction reruns, rounding candidates, verification, replay, density, rank, logs, blind descent, time, and state.

## Full rho/BSGS cost model

Let T be trajectory length, d latent dimension, h observation dimension, b_prec precision bits, K rounded candidates tested, Q_R restrictions, and C_inv replay. Dense RTS work is O(T(d^3+d^2 h+h^3)) per pass in a generic implementation, with O(T d^2) stored covariance state unless recomputation is charged. Set a=log_N(T_model), a_m=log_N(M_model), q=log_N(Q_R(C_RTS(b_prec)+K C_exact+C_inv)+T_replay), and q_m=log_N(M_model+T d^2 b_prec+K+M_inv). With beta=1/5 and common delta,delta_t,r,o,u,ell,ell_m,

lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)

mu=max(a_m,q_m,beta+o,ell_m,u), 0<=r<=o.

Require setup/state <=B^(9/4+o(1)), fresh work/workspace <=B^(5/4+o(1)), lambda,mu<=0.45, and four-size one-sided 95% bounds on exact verified recovery, precision, and cost. Rho/BSGS are 0.50.

## Likely fatal obstruction

Elliptic partial sums are exact nonlinear finite-field states, not a supplied linear-Gaussian process. Learning a useful observation/transition map from labelled trajectories imports source information; Gaussian posterior means lose discrete occurrence ancestry and cannot certify absence. Candidate rounding restores exponential/source-density search. This merges with E08/E09/IDEAS 308/367.

## Proof track

Derive a public low-dimensional state/noise model from elliptic endpoints, prove exact trajectory recovery density and restriction stability, point-faithful rounding, rank, and blind descent.

## Disproof track

Show two distinct source trajectories with identical smoothed sufficient statistics, or a covariance/model parameter that requires labelled source training.

## Positive and negative controls

- Positive: a supplied linear-Gaussian toy model with labelled latent trajectories.
- Negative: nonlinear finite-field transitions, multimodal/aliasing trajectories, shuffled labels, empty/singleton restrictions, precision changes, and blind targets.
- Baselines: Viterbi/particle/observer/AMP, exhaustive candidate rounding, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only frozen model, exact trajectory/source lift, quantified verified recovery, rank d_FB, 100 blind descents, both caps, and lambda,mu<=0.45.
- Falsify on one source-trained model parameter, posterior alias, finite-sample absence claim, cap violation, or complete exponent >=0.50.

## Artifact plan

- ideas/rejected/preallocation/artifacts/20260720-c/g12_model_provenance.md
- ideas/rejected/preallocation/artifacts/20260720-c/g12_trajectory_controls.json
- ideas/rejected/preallocation/artifacts/20260720-c/g12_cost_analysis.md

## Interpretation boundary

This rejects the elliptic RTS transplant, not linear-Gaussian smoothing. A low toy reconstruction error or one verified tuple is not a breakthrough.

## Exactly one next executable action

1. Submit this record and its zero-run snapshot for a Coordinator decision on whether a theorem-only successor may write ideas/rejected/preallocation/artifacts/20260720-c/g12_model_provenance.md; do not create it under the retired snapshot.
