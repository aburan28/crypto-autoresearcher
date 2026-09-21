# ECDLP-IDEA-332 — Stein-score source transport

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_stein_operator_requires_completion_score_or_source_samples`
- Cohort: `20260718-o`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; zero Stein discrepancy, a transported sample, valid relation, or toy witness is not an ECDLP break.

## Falsifiable hypothesis

An endpoint-conditioned Stein operator computable from public elliptic data transports a target-independent proposal distribution to the exact signed source-fibre distribution and yields replayable relation tuples within the P1553 bounds.

## Mechanism-new operation

The screened operation is **derive a score/Stein operator for the conditional source fibre, minimize a kernel Stein discrepancy or apply Stein variational transport, and round transported particles to exact factor tuples**. This merges with IDEAs 079, 104, 143, 282, 302, 316, and 320: the conditional score or Stein kernel encodes completion counts/gradients, while samples from the target already are source witnesses. A discrepancy certifies an aggregate distribution, not a canonical exact point inverse.

## Assumptions

1. A finite-field or discrete Stein identity for the exact source distribution is computable without enumerating completions.
2. Its score/kernel can be evaluated in `B^(5/4)` per fresh target and mixes to exact, not approximate, samples.
3. Each particle rounds to a verified signed tuple with controlled ambiguity on every stratum.
4. Score construction, kernels, particles, iterations, rounding, output, rank, logs, descent, verification, and memory are charged.
5. The same operator works on fresh masked targets without trained source samples.

## Semantic fingerprint

`endpoint_conditioned_source_distribution | public_Stein_score_operator | discrepancy_transport | exact_particle_to_factor_rounding | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H676`, the batched source-fibre generator hypothesis.
3. `inputs/ledger_inventory.json` — imported `P1477`, the serial endpoint-state control.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`, the full-rank aggregate-kernel control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`, the source-edge noncompression boundary.

## Closest primary literature

- Liu, Lee, and Jordan, [A kernelized Stein discrepancy for goodness-of-fit tests](https://proceedings.mlr.press/v48/liub16.html), computes a discrepancy from a supplied target score and samples.
- Liu and Wang, [Stein variational gradient descent](https://proceedings.neurips.cc/paper/2016/hash/b3ba8f1bee1238a2f37603d90b58898d-Abstract.html), transports particles using a supplied differentiable continuous target density/score; it does not provide the hypothesized discrete finite-field score.
- Gorham and Mackey, [Measuring sample quality with kernels](https://proceedings.mlr.press/v70/gorham17a.html), studies when supplied kernel Stein discrepancies detect weak convergence.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies an endpoint predicate, not a conditional source score or exact sampler.

No checked source constructs the discrete finite-field score, transfers the continuous-score guarantees to exact source samples, or supplies the ECDLP descent path; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor decks, proposal, discrete Stein operator, transport schedule, source policy, masks, and verifier.
2. For known-log endpoints, compute the operator without source samples, transport particles, round every accepted particle to exact points, and verify relations.
3. Collect at least `B` independent rows, solve all factor logs, and independently verify them.
4. Apply the identical operator and schedule to fresh scalar-blind masked targets.
5. Substitute logs, remove masks, retain all branches, and accept only `[x]P=Q`.

## Full rho/BSGS cost model

Let setup and memory be `N^a,N^a_m`, `beta=1/5`, reciprocal densities `N^delta,N^delta_t`, score/transport work excluding emission `N^q,N^q_m`, verified rank `N^r`, exact output `N^o`, ambiguity `N^u`, and factor-log completion `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Score construction, all pairwise kernels, particles, iterations, exactification, rejection, output, and verification are charged, with `0<=r<=o`. Promotion requires campaign/setup/state/log exponents at most `0.45`, online at most `0.25`, and `B` verified rows. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponents `0.50`.

## Likely fatal obstruction

A Stein operator is useful because the target score or conditional law is supplied. For the elliptic source fibre, evaluating a score or one-step completion ratio is the missing counting/router oracle. Approximate distributional convergence does not return an exact witness, and exact mixing can retain rho-scale rare-event cost.

## Proof track

Construct an endpoint-only discrete Stein operator, prove exact polynomial mixing and all-strata rounding, then prove relation rank, factor logs, blind descent, and `lambda,mu<=0.45`.

## Disproof track

Reduce one score evaluation to a completion count/source query, exhibit score-equal distributions with different labelled supports, or charge particle/kernel state beyond the gates.

## Positive and negative controls

- Positive: supplied discrete target distributions with known scores must pass discrepancy and exact sampling checks.
- Negative: equal aggregate scores under permuted source labels and approximate-only samplers must not emit preferred factor points.
- Baselines: IDEAs 079/104/143/282/302/316/320, rejection sampling, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with source-free score and exact-mixing theorems, 1,000 verified rows and 100 blind descents per large size, P1553 rectangles, and complete `lambda,mu<=0.45`.
- Falsify if a completion count/source sample is input, exact mixing reaches `N^0.50`, one stratum is missed, or either complete exponent reaches `0.50`.
- Low discrepancy for supplied samples is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-332/score_completion_oracle_receipt.md`
- `ideas/artifacts/ECDLP-IDEA-332/label_permutation_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-332/independent_stein_verifier.py`
- `ideas/artifacts/ECDLP-IDEA-332/cost_analysis.md`

## Interpretation boundary

This rejects the declared Stein-score route, not Stein methods generally. Distributional fit, a sampled planted tuple, or relation validity is not a complete ECDLP algorithm or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-332/score_completion_oracle_receipt.md` expressing one proposed discrete score evaluation as explicit source-completion counts and charging them.
