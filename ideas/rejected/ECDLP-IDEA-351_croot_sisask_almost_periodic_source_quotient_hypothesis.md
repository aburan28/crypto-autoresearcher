# ECDLP-IDEA-351 — Croot–Sisask almost-periodic source quotient

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_approximate_almost_periods_do_not_preserve_singleton_exact_relations`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; an almost period or approximate convolution match is not an ECDLP break.

## Falsifiable hypothesis

Croot–Sisask sampling finds a target-independent quotient of factor-deck convolution profiles whose classes preserve exact restricted nonemptiness and admit bounded correction, so logarithmic bisection recovers one signed source inside the P1553 gates.

## Mechanism-new operation

The screened operation is **sample almost periods of factor-deck convolutions, quotient target shifts with nearly equal profiles, and exactly correct the residual while self-reducing to sources**. It is distinct only if approximation never erases a singleton relation and exact correction is smaller than the original convolution/source reporter.

Minimum-interface correction: counts, all witnesses, and a canonical inverse are unnecessary. A target-labelled, subset-stable exact existence bit under arbitrary dyadic deck restrictions, with `O(log B)` bisection calls and all restriction/update costs charged, suffices to recover one tuple.

## Assumptions

1. Sparse curve factor decks satisfy a useful small-doubling, energy, or local almost-period hypothesis uniformly.
2. The sampled quotient is target-independent and scalar-blind.
3. Approximate profile equality preserves zero-versus-nonzero relation support.
4. Exact residual correction preserves zero-versus-nonzero under every dyadic restriction, so bisection returns one signed tuple across collision and exceptional strata.
5. Samples, exceptional shifts, correction, output, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`factor_deck_convolution | Croot_Sisask_sampled_almost_periods | target_shift_quotient | subset_stable_exact_restricted_support_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H673`; coordinate families selected by additive energy failed to transfer a stable relation-yield or total-work advantage.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1432-NO-PROSPECTIVE-HIGH-ENERGY-PROMOTION`; training energy did not transfer across held-out pair, triple, four-sum, or relation gates.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1423-FULL-PHASE-NONLINEAR-GAP`; approximate/phase structure did not construct the exact nonlinear membership and source query.
4. `inputs/ledger_inventory.json` — imported `ECFG-H676`; the required exact public source-fibre generator remained full-rank and above the campaign gate.
5. `inputs/ledger_inventory.json` — imported `ECFG-H675`; exact source-resolving membership, not an almost-periodic norm or moment, is the missing operation.

## Closest primary literature

- Croot and Sisask, [A probabilistic technique for finding almost-periods of convolutions](https://arxiv.org/abs/1003.2978), proves norm-level almost-periodicity under additive-structure hypotheses; it does not preserve singleton support or return contributors.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies exact relation equations and no bridge from approximate mass to exact point sources.

No checked source gives a complete exact ECDLP route; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, coloured decks, convolution representation, sampler, quotient, correction, masks, and verifier.
2. Build target-independent sampled almost-period state without scalar coordinates or relation-event input.
3. For known-log targets, query restricted exact existence, bisect to one complete signed tuple, and replay it.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Apply the identical quotient/correction to fresh `Q+[t]P` targets.
6. Substitute logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge sampling, exceptional shifts, approximation precision, correction, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, correction/query `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Require `0<=r<=o`, setup/state at most `B^(9/4)`, fresh query at most `B^(5/4)`, and complete `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50`; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Random-like `N^0.2` decks need not have useful almost-period sets. More decisively, an approximation error of one can erase the unique exact relation. Repairing that bit for every restriction restores the exact convolution, a scalar Fourier table, or P1553's missing decision/source oracle. A prime-order group supplies no nontrivial exact subgroup quotient.

## Proof track

Prove a uniform almost-period theorem with zero restricted-support error, construct the bounded exact decision correction and bisection self-reduction, and derive complete sub-gate costs.

## Disproof track

Construct equal-bound convolution profiles with different singleton support, prove the exceptional set is source-sized, or show exact correction computes the original source fibre.

## Positive and negative controls

- Positive: dense small-doubling cyclic sets with planted exact periods and named contributors.
- Negative: matched profiles differing at one support point, random prime-order decks, and source-permuted convolutions.
- Baselines: IDEAs 027/048/118/340/348, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with zero false positives and negatives over every restriction, charged bisection to exact source replay, 1,000 independent rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and `lambda,mu<=0.45`.
- Falsify on a same-profile/different-support family for which every public exact correction or section exceeds the setup/query gates, a source-sized correction, a scalar-index character table, or either exponent at least `0.50`.
- Approximate agreement or a correct toy relation cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-351/almost_period_exactness_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-351/singleton_support_counterexamples.json`
- `ideas/artifacts/ECDLP-IDEA-351/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-351/cost_analysis.md`

## Interpretation boundary

This rejects the exact-source adaptation, not Croot–Sisask almost-periodicity. All finite checks would be toy, heuristic, model-bound, and novelty-unverified. Approximation or correctness is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-351/singleton_support_counterexamples.json` containing the smallest matched convolution profiles with identical preregistered almost-period bounds and different exact singleton support.
