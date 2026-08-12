# Pre-ID duplicate draft — Hutchinson trace source estimator

## Status and claim labels

- Provisional ID: `PREID-20260723-a-R04`; no canonical ID allocated.
- Disposition: `merged_rejected_stochastic_aggregate_without_occurrence_identity`.
- Class/risk: measurement / conservative.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; an unbiased estimate, valid row, or verifier pass is not an ECDLP result.

## Falsifiable hypothesis

For generic prime-order ECDLP, an endpoint-derived source-incidence operator has trace statistics
that exactly distinguish empty restricted fibres from nonempty ones. Hutchinson probes provide
the decision and a charged self-reduction to signed occurrences, enabling complete factor logs
and 100 blind descents with exponents at most `0.45`.

## Mechanism-new operation

Hutchinson estimation averages quadratic forms of random sign vectors to estimate the trace of a
supplied matrix. It counts here only if endpoint-only operator products give zero-error restricted
existence, with all randomness and failure probability charged, and conditioning replays exact
source occurrences. Trace estimation after materializing incidence is a measurement control.

## Assumptions

1. Public endpoints define exact operator-vector products without source rows.
2. Trace separates zero from the smallest positive restricted fibre with certified zero error.
3. Probe count and precision remain inside the online cap after union bounds over restrictions.
4. Self-reduction retains signs, repetitions, and source occurrence identities.
5. Target-independent probes and state are reused without selection leakage on blind targets.

## Semantic fingerprint

`public_endpoint_incidence_operator | random_sign_trace_quadratic_forms | exact_zero_nonzero_fibre_decision | charged_source_self_reduction | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260721-c_K09_ams_moment_source_sketch_preid_duplicate.md` — random moments are aggregates without source identity.
2. `ideas/rejected/preallocation/20260719-b_B11_frequent_directions_source_sketch_preid_duplicate.md` — covariance sketches preserve approximate energy, not occurrences.
3. `ideas/rejected/preallocation/20260721-a_I04_johnson_lindenstrauss_exact_margin_preid_duplicate.md` — approximate projection cannot provide exact empty-fibre semantics.
4. `ideas/deferred/ECDLP-IDEA-053_aggregate_moment_large_prime_decoder_hypothesis.md` — aggregate moments collide across source configurations.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — owns exact restricted existence plus signed replay.

## Closest primary literature

- Hutchinson, [A Stochastic Estimator of the Trace of the Influence Matrix for Laplacian Smoothing Splines](https://doi.org/10.1080/03610918908812806), estimates the trace of a supplied matrix by random probes.
- Semaev, [Summation polynomials](https://eprint.iacr.org/2004/031), does not supply the source-incidence operator.
- Shoup, [generic lower bounds](https://www.shoup.net/papers/dlbounds1.pdf), controls generic costs.

The paper supplies an estimator, not an exact source predicate or inverse; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze `B=N^(1/5)`, operator, probe distribution, seed policy, threshold, restrictions, strata, and verifier.
2. Build operator access and target-independent probes within `B^(9/4+o(1))`, with no source catalogue or scalar labels.
3. For known-log targets, decide every restriction with certified zero error, self-reduce to signed points, and verify the elliptic sum.
4. Collect at least `max(d_FB+32,1000)` verified independent rows, rank `d_FB`, and all factor logs.
5. Reuse frozen state on 100 fresh masked targets, recover sources, subtract masks, and verify every scalar.
6. Charge operator construction, probes, variance reduction, union-bound repetitions, failures, self-reduction, output, rank, logs, bits, and memory.

## Full rho/BSGS cost model

With `beta=1/5`, let `a,a_m` be setup/state; `delta,delta_t` reciprocal densities;
`q,q_m` probe-decision work/workspace; `r` rank credit; `o` output; `u` ambiguity/failure
repetition; and `ell,ell_m` factor-log costs. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require `lambda,mu<=0.45`,
setup/state `<=B^(9/4+o(1))`, and fresh work/workspace `<=B^(5/4+o(1))`.
Rho expected time and BSGS time/memory remain exponent `0.50`.

## Likely fatal obstruction

Trace is an aggregate. Finite probes have variance and cannot certify exact zero versus one rare
source under arbitrary restrictions. Exact trace evaluation requires the source operator, while
equal traces can hide different occurrence sets and signs.

## Proof track

Prove an endpoint-only operator, an integer spectral gap for every restriction, deterministic or
zero-error subcap probing, and exact signed self-reduction through full descent.

## Disproof track

Construct equal-trace different-source operators, a rare fibre below the estimator error, a
source-bearing product, selection leakage, replay ambiguity, or a complete exponent `>=0.50`.

## Positive and negative controls

- Positive: diagonal toy operators with planted trace gaps and labelled source inverses.
- Negative: equal-trace permutations, rank-one rare sources, empty fibres, cancellation,
  exceptional strata, seed reuse, and fresh blind targets.
- Baselines: AMS, Frequent Directions, P1553 R4, rho, and BSGS.
- Unbiasedness is only toy/model-bound measurement evidence.

## Quantitative promotion and falsification gates

- Promote only with zero semantic errors at four sizes/all strata, a proved zero-error gap,
  full rank/logs, 100 blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one equal-trace collision, nonzero error probability, hidden source product, cap
  violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260723-a/r04_operator_trace_audit.md`
- `ideas/rejected/preallocation/artifacts/20260723-a/r04_equal_trace_counterexamples.json`
- `ideas/rejected/preallocation/artifacts/20260723-a/r04_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Hutchinson estimation. Trace accuracy, correctness, and valid
relations remain toy, heuristic, model-bound, and novelty-unverified.

## Exactly one next executable action

1. Construct the smallest pair of restricted toy source operators with equal trace but different occurrence support and record whether the claimed decision distinguishes them without source labels.
