# Pre-ID duplicate draft — Girsanov likelihood endpoint-source bridge

## Status and claim labels

- Class: `girsanov_likelihood_endpoint_source_bridge`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_radon_nikodym_likelihood_is_missing_source_predicate_and_sampling_cannot_certify_exact_zero`
- Cohort: `20260719-a`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: none; rejected before dispatch
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid change-of-measure identity or sampled relation is not an ECDLP break.

## Falsifiable hypothesis

A reference walk on partial source tuples admits an endpoint-derived Girsanov likelihood whose changed measure is the exact restricted endpoint-conditioned path law; exact likelihood queries and path replay return source occurrences below rho and BSGS.

## Mechanism-new operation

The screened operation is **define a source-blind reference walk, compute an endpoint-only Radon–Nikodym likelihood, change measure to the bridge conditioned on the target endpoint, and replay a conditioned path to five labelled occurrences**. This is likelihood-ratio path inversion, not generic resampling.

## Assumptions

1. The likelihood and normalizer are computable without evaluating the hidden completion predicate.
2. Absolute continuity covers every valid signed/repeated stratum.
3. Exact zero versus nonzero restricted mass is decidable, not merely estimable.
4. Path replay preserves occurrence labels with bounded ambiguity.
5. Likelihood, normalization, sampling/error, output, rank, logs, descent, time, and memory are charged.

## Semantic fingerprint

`source_blind_partial_tuple_walk | endpoint_radon_nikodym_likelihood | exact_conditioned_bridge | labelled_path_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`; the changed measure must still generate exact public sources.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; an endpoint score requires a point-faithful inverse.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; the source generator and transposed return remain unresolved.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1409-LOSSLESS-DAG-EDGE-BARRIER`; exact path replay stores source-distinct edges.
5. `inputs/ledger_inventory.json` — imported `P1477`; explicit backward endpoint states remain dense.

## Closest primary literature

- Girsanov, [On transforming a certain class of stochastic processes by absolutely continuous substitution of measures](https://doi.org/10.1137/1105027), changes measure for supplied processes and densities; it does not construct an exact combinatorial endpoint likelihood or occurrence inverse.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), gives the endpoint relation but no exact bridge likelihood.

No checked source supplies the proposed exact endpoint-source bridge; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, restrictions, reference walk, likelihood/normalizer rule, exact-arithmetic policy, replay convention, and verifier.
2. Build target-independent reference/likelihood state within `B^(9/4+o(1))` without source edges.
3. For known-log targets, decide exact restricted mass and recover a verified five-occurrence path, charging retries or bisection.
4. Collect at least `B` independent verified rows, charge variance/normalization/output, and solve factor logs.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`.
6. Replay a path, substitute logs, remove `t`, and verify `[x]P=Q`.
7. Charge likelihood computation, normalization, exact-zero testing, path output, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Require `0<=r<=o`, setup/state no more than `B^(9/4+o(1))`, a complete fresh restricted query no more than `B^(5/4+o(1))`, and `lambda,mu<=0.45`. Pollard rho expected time and BSGS time/memory have exponent `0.50`.

## Likely fatal obstruction

The Radon–Nikodym derivative for conditioning on a rare exact endpoint is the missing path-count/source predicate. Sampling or likelihood estimates cannot certify a worst-case exact zero, while an exact Doob/Girsanov bridge needs dense backward state or source paths. This meets IDEAs 104, 147, 302, 316, and 332.

## Proof track

Construct an exact endpoint-only likelihood and normalizer, prove exact restriction mass and labelled replay with controlled variance/ambiguity, then certify full descent.

## Disproof track

Reduce likelihood evaluation to Query2P1, show absolute continuity misses a valid stratum, exhibit equal retained likelihoods with different source paths, or exceed a gate.

## Positive and negative controls

- Positive: supplied finite Markov bridges with exact transition densities and planted paths.
- Negative: zero-mass restrictions, rare paths, equal endpoint marginals with different trajectories, support mismatch, repeated occurrences, and blind targets.
- Baselines: IDEAs 104/147/302/316/332, explicit backward DP, Query2P1, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with exact endpoint likelihood/zero testing, `1,000` verified rows, `100` blind descents, zero missed supports, caps, and `lambda,mu<=0.45`.
- Falsify on one hidden completion oracle, support miss, equal-state/different-path collision, cap violation, or exponent at least `0.50`.
- A sampled valid toy path or correct likelihood identity is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-432/likelihood_source_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-432/equal_likelihood_path_collisions.json`
- `ideas/artifacts/ECDLP-IDEA-432/restriction_bridge_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-432/cost_analysis.md`

## Interpretation boundary

This rejects the screened Girsanov endpoint-source bridge, not change-of-measure theory. Prospective evidence is toy, heuristic, model-bound, and novelty-unverified; sampling a relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-432/likelihood_source_obligations.md` and classify every reference transition, likelihood factor, normalizer, exact-zero query, replay edge, restriction decision, and occurrence label.
