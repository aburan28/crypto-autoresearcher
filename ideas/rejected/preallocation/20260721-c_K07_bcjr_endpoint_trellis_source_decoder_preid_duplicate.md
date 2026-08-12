# Pre-ID duplicate draft — BCJR endpoint-trellis source decoder

## Status and claim labels

- Prospect: `20260721-c-K07`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: trellis_posterior_decoder / representation-changing / pre-ID screen.
- State: merged_rejected_supplied_trellis_and_posterior_not_exact.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a posterior or decoded path is not an ECDLP result.

## Falsifiable hypothesis

Compile signed elliptic partial sums into a compact target-independent trellis, run BCJR forward/backward recursions to obtain exact symbol marginals for every restriction, and backtrack one exact source for full descent below rho and BSGS.

## Mechanism-new operation

The native operation computes a posteriori state/symbol probabilities on a supplied finite-state channel trellis. It counts only if the trellis and local likelihoods are endpoint-derived, exact over finite fields, and marginal positivity is biconditional with a labelled source path; decoding a supplied source trellis is a control.

## Assumptions

1. A compact trellis captures every signed source path without `B^m` state.
2. Branch metrics are public and do not invoke source-existence labels.
3. Forward/backward aggregation has exact zero/nonzero semantics without cancellation or floating error.
4. Positive marginals backtrack to signed occurrences on all strata.
5. Frozen state supports fresh masked targets and independent rows.

## Semantic fingerprint

`public_endpoint_compact_trellis | BCJR_forward_backward_marginals | exact_restricted_path_existence | posterior_backtrack_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — subset-stable exact source return.
2. `ideas/rejected/ECDLP-IDEA-120_myhill_nerode_serial_s3_state_quotient_hypothesis.md` — exact finite-state quotients retain source-sized distinguishability.
3. `ideas/rejected/ECDLP-IDEA-226_polar_successive_cancellation_source_decoder_hypothesis.md` — likelihood computation is the original partition/source problem.
4. `ideas/rejected/preallocation/20260720-a_E08_viterbi_source_trellis_preid_duplicate.md` — best-path decoding starts from a supplied trellis.
5. `ideas/rejected/preallocation/20260720-c_G12_rts_smoother_source_trajectory_preid_duplicate.md` — smoothing consumes a supplied transition/observation model.

## Closest primary literature

- Bahl, Cocke, Jelinek, and Raviv, [Optimal decoding of linear codes for minimizing symbol error rate](https://doi.org/10.1109/TIT.1974.1055186), gives forward/backward APP decoding on a supplied trellis/channel model.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies equations rather than a compact trellis.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source compiles the ECDLP trellis or proves exact occurrence backtracking; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, trellis states/branches, branch semiring, restrictions, charts, and verifier.
2. Construct the trellis and certify path/source biconditionality from endpoints only.
3. For known-log targets, run exact restricted forward/backward passes, backtrack a labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve every factor log.
5. Reuse unchanged trellis for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge trellis construction, all branch metrics, passes, normalization/cancellation repair, backtracking, density, rank, logs, bit time, and memory.

## Full rho/BSGS cost model

Charge trellis construction/state in `a,a_m`, forward/backward restriction/backtrack in `q,q_m`, and path/marginal ambiguity in `o,u`. With `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, exact arithmetic, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

BCJR is linear in the supplied trellis size. Exact partial elliptic sums have source-distinct product state or merge states with different future completions. A compact endpoint quotient loses path provenance; exact marginals require the same source transition matrix being sought. Probabilistic APPs also do not certify empty restrictions, and finite-field sums can cancel.

## Proof track

Construct a compact endpoint-only trellis, prove future-equivalence and zero/nonzero semantics for every restriction, and give exact all-strata backtracking inside the cost caps.

## Disproof track

Apply a Myhill–Nerode state-distinguishability audit, trace branch origins, test modular cancellation and empty fibres, and falsify on source-sized state or missing backtrack.

## Positive and negative controls

- Positive: supplied small labelled trellises with exact semiring marginals.
- Negative: source-distinct equal-endpoint states, cancellation, rare paths, empty restrictions, and fresh targets.
- Baselines: Viterbi, polar decoding, explicit dynamic programming, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with a compact endpoint-only trellis theorem, exact zero semantics, four sizes, zero errors, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied transitions, state explosion, cancellation, false marginal, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k07_trellis_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k07_bcjr_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k07_cost_analysis.md`

## Interpretation boundary

This rejects the compact endpoint trellis compiler, not BCJR. Any decoded toy path remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
