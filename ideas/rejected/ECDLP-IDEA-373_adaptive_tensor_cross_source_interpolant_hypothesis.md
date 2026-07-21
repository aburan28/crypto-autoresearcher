# ECDLP-IDEA-373 — Adaptive tensor-cross source interpolant

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- Top lane: `representation-changing`
- State: `merged_rejected_cross_oracle_is_exact_query2p1_and_rare_zero_mask_has_no_low_rank_guarantee`
- Cohort: `20260718-r`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: retired zero-run preflight under `review_required`; execution prohibited
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; fitting a toy tensor or validating sampled entries is not an ECDLP break.

## Falsifiable hypothesis

The exact elliptic relation mask admits an endpoint-queryable low-rank tensor-train representation recoverable by adaptive tensor-cross interpolation, with restriction-stable zero decisions and exact source bisection inside the P1553 gates.

## Mechanism-new operation

The screened operation is **probe adaptively chosen tensor fibres, select cross pivots, reconstruct an exact tensor-train interpolant of the relation mask, and use restricted subtensor contractions to bisect one source tuple**. It is distinct only if each probe is cheaper than exact Query2P1, exact rank remains subgate on all targets and strata, pivot selection is source-blind, and rare zeros cannot be missed by approximation.

## Assumptions

1. An exact endpoint relation indicator or nonnegative zero mask has target-uniform tensor-train rank below the setup/state gate.
2. Entries can be queried without enumerating complement pairs or invoking exact restricted existence.
3. Adaptive cross pivots are public and preserve arbitrary deck restrictions and fresh-target updates.
4. Exact contractions decide nonempty restricted fibres and return one signed tuple on every stratum.
5. Entry probes, pivots, interpolation arithmetic/precision, rank growth, restrictions, output, factor logs, descent, verification, and memory are charged.

## Semantic fingerprint

`determinant_or_sum_zero_mask | adaptive_TT_cross_pivots | exact_low_rank_interpolant | subset_stable_zero_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-H663`; low-rank public kernels are hypothesized but not shown to preserve exact source fibres.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`; tested recall-preserving truncations remained full pair-state rank.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1420-ZERO-PRODUCT-NO-PROMOTION`; an exact zero mask retained all outer-pair entries and adaptive witness descent did not promote it.
4. `inputs/ledger_inventory.json` — imported `ECFG-H675`; a source-resolving compact circuit is the missing object.
5. `inputs/ledger_inventory.json` — imported `ECFG-H676`; target-uniform source-fibre generation remains unconstructed.

## Closest primary literature

- Oseledets and Tyrtyshnikov, [TT-cross approximation for multidimensional arrays](https://doi.org/10.1016/j.laa.2009.07.024), reconstructs approximate low-rank tensors from selected entries under rank/conditioning assumptions.
- Savostyanov and Oseledets, [Fast adaptive interpolation of multi-dimensional arrays in tensor train format](https://doi.org/10.1002/nla.682), develops adaptive tensor-train cross interpolation for entry-queryable arrays.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), defines endpoint relations but no cheap exact mask-entry oracle or low-rank theorem.

No checked source proves exact low tensor-train rank, rare-zero preservation, or a cheap elliptic mask oracle; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, pairwise-disjoint decks, tensor indexing, exact mask, cross algorithm, pivot rule, target masks, and verifier.
2. Build a target-independent exact tensor-train representation using only charged endpoint probes and no source-labelled pivot advice.
3. On known-log targets, update the representation, contract restricted subtensors, bisect coordinates, recover one tuple, and replay it by group addition.
4. Collect at least `B` independent verified rows, solve factor logs, and independently verify them.
5. Apply the unchanged entry, interpolation, and bisection rules to fresh scalar-blind `Q+[t]P` targets.
6. Recover a tuple, substitute factor logs, remove `t`, retain ambiguity, and verify `[x]P=Q`.
7. Charge every entry probe, pivot search, rank adaptation, exact arithmetic, target update, contraction, source output, rank, logs, descent, verification, bit time, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, query work excluding output `N^q,N^q_m`, verified rank credit `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `0<=r<=o`. Setup/state must be at most `B^(9/4+o(1))`; a fresh target must be at most `B^(5/4+o(1))`; promotion requires `lambda,mu<=0.45`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`.

## Likely fatal obstruction

Tensor cross assumes a cheap entry oracle and approximate low rank. For the elliptic mask, an exact entry or fibre probe is the P1553 Query2P1 operation being sought, while rare zero entries can have negligible approximation mass but determine all valid sources. Exact post-Fermat or indicator tensors can have target-dependent full rank, and adaptive source-conditioned pivots become post-hoc selectors. This merges with IDEAs 060, 253, 324, 331, and 341 unless an exact rank-and-oracle theorem changes the representation.

## Proof track

Prove a target-uniform exact tensor-train rank bound, construct every entry probe below Query2P1 cost, and prove restriction-stable zero/source semantics with complete exponents at most `0.45`.

## Disproof track

Exhibit target/deck families with full flattening rank or indistinguishable sampled crosses but different rare restricted zeros, or reduce each exact probe to Query2P1.

## Positive and negative controls

- Positive: supplied exact low-rank tensors with planted nonzero fibres and externally labelled sources.
- Negative: singleton zeros, adversarial full-rank flattenings, equal sampled crosses with different unsampled witnesses, source-conditioned pivots, all P1553 strata, and blind targets.
- Baselines: IDEAs 060/253/324/331/341, exact pair tables, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a proved exact rank/oracle theorem, source-blind pivots, exact restriction-stable bisection, 1,000 rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on a Query2P1 entry oracle, full-rank flattening, one missed rare zero or stratum, source-labelled pivots, source-sized exact repair, or either exponent at least `0.50`.
- Accurate approximation or interpolation of a supplied toy tensor is only a control.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-373/exact_tt_cross_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-373/rare_zero_rank_cases.json`
- `ideas/artifacts/ECDLP-IDEA-373/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-373/cost_analysis.md`

## Interpretation boundary

This rejects the screened entry-oracle route, not tensor-cross interpolation. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A fitted tensor is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-373/exact_tt_cross_obligations.md` and prove whether exact mask entries and rank bounds can be obtained without solving Query2P1.
