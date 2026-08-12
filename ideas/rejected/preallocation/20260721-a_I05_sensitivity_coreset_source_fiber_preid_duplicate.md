# Pre-ID duplicate draft — Sensitivity-coreset source fiber

## Status and claim labels

- Prospect: `20260721-a-I05`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: sampling_compression / representation_changing / representation-changing pre-ID screen.
- State: scoped_rejected_approximate_objective_and_supplied_source_functions.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; an objective approximation or toy relation is not a breakthrough.

## Falsifiable hypothesis

Assign endpoint-derived sensitivities to partial source constraints and retain a weighted coreset that preserves every restricted nonempty fiber and permits exact source replay, factor logs, and blind descent below rho/BSGS.

## Mechanism-new operation

Sensitivity sampling compresses a supplied family of cost functions while approximately preserving their total objective over all queries. It counts only if the weights are endpoint-derived before source enumeration and preserve exact zero-versus-nonzero fiber semantics plus occurrence labels; clustering a supplied catalogue is a control.

## Assumptions

1. Per-constraint sensitivities are computable from public endpoints without listing sources.
2. The coreset preserves exact fiber nonemptiness, not merely an approximate cost.
3. Weights and samples retain duplicates, signs, restrictions, and exceptional strata.
4. A positive coreset query replays an exact signed tuple with charged probability/error.
5. One target-independent sample supports known-log relations and fresh blind targets.

## Semantic fingerprint

`public_endpoint_constraint_sensitivity | weighted_coreset_sampling | exact_restricted_fiber_nonemptiness | sample_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260720-a_E01_kll_quantile_source_compactor_preid_duplicate.md` — a summary of supplied values is not exact source state.
2. `ideas/rejected/preallocation/20260720-a_E02_minhash_bottomk_source_resemblance_preid_duplicate.md` — sampling preserves similarity, not exact occurrences.
3. `ideas/rejected/preallocation/20260720-a_E12_reservoir_source_sampler_preid_duplicate.md` — uniform samples miss rare exact fibers.
4. `ideas/rejected/preallocation/20260719-b_B11_frequent_directions_source_sketch_preid_duplicate.md` — approximate objectives lose source labels.
5. `ideas/rejected/preallocation/20260720-d_H12_lloyd_centroid_source_quantizer_preid_duplicate.md` — clustering summaries are model state, not equality witnesses.

## Closest primary literature

- Feldman and Langberg, [A unified framework for approximating and clustering data](https://arxiv.org/abs/1106.1379), constructs coresets for supplied positive-function objectives with approximation guarantees.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies exact endpoint equations, not sensitivities.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source gives an exact source-returning elliptic coreset; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, constraint family, sensitivity rule, random seed policy, signed strata, restrictions, and verifier.
2. Compute weights and sample state from public endpoints within the setup cap, without enumerating sources or invoking `Query2P1`.
3. For each known-log target, answer every restricted fiber query exactly, replay labelled signed points, verify their sum, and record only verified rows.
4. Preserve misses/dependencies; for actual `d_FB`, collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged state on `Q+[t]P`, replay, compute the scalar, and verify `[x]P=Q`.
6. Charge sensitivity computation, sampling, weights, amplification, restrictions, replay, density, rank, logs, blind descent, bit time, and peak memory.

## Full rho/BSGS cost model

Let `a,a_m` charge sensitivity/sample setup and `q,q_m` charge exact queries, amplification, fallback, and replay. For `B=N^beta`, `beta=1/5`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`.

All approximation error and missed-fiber fallback belong to `u`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`, versus rho/BSGS `0.50`.

## Likely fatal obstruction

Coresets preserve aggregate objectives of supplied functions. A certified two-sided relative `(1+-epsilon)` guarantee with `epsilon<1` would preserve zero versus positive exactly, so approximation alone is not a no-go. The valid obstruction is stronger: the guarantee must hold uniformly over all adaptive restrictions, including rare singleton fibers; their total sensitivity/support can force source-sized state, computing sensitivities already assumes the missing source functions, and an objective value still lacks labelled occurrence replay.

## Proof track

Prove an endpoint-only two-sided relative guarantee for every adaptive restriction, bound total sensitivity and support below the caps even for singleton fibers, and preserve exact all-occurrence replay with complete costs.

## Disproof track

Construct rare singleton fibers and equal-cost collisions; falsify if uniform coverage forces source-sized total sensitivity/support, if sensitivities require source functions, or if labelled replay/fallback enumerates the source deck.

## Positive and negative controls

- Positive: supplied clustering/function instances with standard relative-error coresets and planted labels.
- Negative: singleton positive fibers among zeros, duplicate constraints, shuffled labels, empty restrictions, and fresh targets.
- Baselines: full data, reservoir/KLL/MinHash sketches, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require a uniform two-sided guarantee with `epsilon<1`, sub-cap total sensitivity/support across all restrictions, zero-error exact nonemptiness and lift, recorded failure at most `2^-80`, four increasing sizes, full rank from `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on a missed singleton, source-sized sensitivity/support, supplied source functions, lost labels, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i05_zero_set_preservation_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i05_coreset_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i05_cost_analysis.md`

## Interpretation boundary

This rejects an exact ECDLP coreset, not ordinary coreset approximation. Toy results remain heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not sample a coreset.
