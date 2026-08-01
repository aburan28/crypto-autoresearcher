# ECDLP-IDEA-358 — Slice-rank diagonal source isolation

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- Top lane: `-`
- State: `merged_rejected_aggregate_rank_has_no_source_witness_extractor`
- Cohort: `20260718-q`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none; rejected before dispatch`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a low slice-rank bound or valid diagonal restriction is not an ECDLP break.

## Falsifiable hypothesis

The six-list Abel-Jacobi relation indicator has an endpoint-specialized slice decomposition whose restricted nonvanishing can be decided exactly and bisected to factor-base sources within the P1553 gates.

## Mechanism-new operation

The screened operation is **restrict the six-list relation tensor and evaluate a bounded slice decomposition as an exact nonvanishing decision oracle for dyadic source subsets**. It is distinct only if the decomposition is built from endpoint arithmetic, not from the source table, and restrictions preserve exact nonemptiness rather than only an aggregate rank bound.

Minimum-interface correction: the decomposition need not expose a term. A target-labelled, subset-stable exact nonvanishing bit under arbitrary dyadic deck restrictions, with `O(log B)` charged slice queries, suffices to bisect one signed tuple.

## Assumptions

1. The relation tensor and restriction family are computable directly from public curve, factor-base, and target data.
2. The restricted tensor has sub-source-size slice rank uniformly across every source stratum.
3. Adaptive slice queries decide exact restricted nonvanishing without expanding the tensor, enabling logarithmic source bisection.
4. Restricted nonvanishing is exact and subset-stable, so bisection recovers all labels and signs of one tuple with no ancestry dictionary.
5. Decomposition, restriction, adaptive queries, output, verification, rank, logs, descent, and memory are charged.

## Semantic fingerprint

`six_list_abel_jacobi_indicator | target_specialized_slice_rank_decomposition | subset_stable_exact_nonvanishing_decision | dyadic_source_bisection | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`; a transformed exact source operator retained full-rank state.
2. `inputs/ledger_inventory.json` — imported `ECFG-H675`; an endpoint-derived exact source tensor or circuit remains the missing object.
3. `inputs/ledger_inventory.json` — imported `ECFG-H676`; aggregate algebraic structure did not supply arithmetic source-fibre generation.
4. `inputs/ledger_inventory.json` — imported `ECFG-P1434-GENERATIVE-RULE-POSITIVE-CONTROL`; exact relation replay with supplied scalar inputs is only a positive control.
5. `inputs/ledger_inventory.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`; source-resolved reporting preserves the witness burden.

## Closest primary literature

- Blasiak et al., [On cap sets and the group-theoretic approach to matrix multiplication](https://doi.org/10.19086/da.1245), develops slice-rank bounds for structured tensors; it does not provide a witness extractor for an implicitly represented Abel-Jacobi tensor.
- Ellenberg and Gijswijt, [On large subsets of finite vector spaces with no three-term arithmetic progression](https://doi.org/10.4007/annals.2017.185.1.8), obtains global combinatorial bounds from polynomial tensors rather than exact labelled source recovery.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies a relation predicate but not an endpoint-only slice decomposition or diagonal inverse.

No checked source supplies the required adaptive source extractor; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, six-list tensor convention, restriction family, slice compiler, source inverse, masks, and verifier.
2. Build target-independent slice state or a bounded target update without enumerating relation tuples.
3. Query restricted exact nonvanishing for known-log targets, bisect one signed tuple, and replay its group sum.
4. Collect `B` independent rows, solve factor logs, and verify them against the factor base.
5. Repeat the identical diagonal-isolation process on fresh masked targets.
6. Substitute recovered logs, remove masks, retain ambiguity, and verify `[x]P=Q`.
7. Charge tensor/decomposition construction, restrictions, adaptive probes, source output, verification, rank, logs, descent, and memory.

## Full rho/BSGS cost model

With `B=N^(beta)`, `beta=1/5`, and exponents `a,a_m,delta,delta_t,q,q_m,r,o,u,ell,ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Here `a` charges decomposition construction, `q` includes adaptive slice queries plus target/restriction updates, `r` is certified sharing, `o` is exact source output, and `u` is residual ambiguity. Require `0<=r<=o`, setup/state `<=B^(9/4)`, fresh query `<=B^(5/4)`, and complete exponents `<=0.45`. Rho and BSGS time are exponent `0.50`; BSGS memory is `0.50`.

## Likely fatal obstruction

Slice rank bounds an aggregate tensor; it supplies neither an exact evaluator of restricted nonvanishing nor an endpoint-only construction of such an evaluator. Direct term extraction and point labels are stronger than necessary. In the audited route, building restrictions from explicit relation entries reinstates the source tensor, while retaining decomposition state exact under arbitrary dyadic restrictions reinstates source-sized ancestry. The allowed `O(log B)` self-reduction therefore still lacks a sub-gate decision query.

## Proof track

Prove an endpoint-only decomposition theorem, subset-stable exact nonvanishing with charged bisection, and complete sub-gate bounds for all strata and fresh targets.

## Disproof track

Exhibit restricted tensors with identical available slice data but different exact nonvanishing and no sub-gate correction, prove decomposition/restriction requires tensor materialization, or show the charged decision queries reach the source witness surface.

## Positive and negative controls

- Positive: a supplied diagonal tensor whose low-rank decomposition includes exact labelled terms.
- Negative: source-permuted tensors with identical slice ranks and aggregate restrictions but different witnesses.
- Baselines: IDEAs 105/152/234/324/326, P1553-FD-R2, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only construction, zero source errors, 1,000 exact rows, 100 blind descents, and complete time/memory exponents at most `0.45`.
- Falsify on an aggregate-equivalent/different-source family whose every public adaptive correction or diagonal section exceeds the gates, required tensor materialization, ancestry-sized state, or complete exponent at least `0.50`.
- A slice-rank inequality, nonvanishing certificate, or toy diagonal is insufficient.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-358/slice_decomposition_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-358/diagonal_collision_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-358/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-358/cost_analysis.md`

## Interpretation boundary

This rejects the current source-invertible adaptation, not slice-rank theory. All prospective checks are toy, heuristic, model-bound, and novelty-unverified. Aggregate rank is not a breakthrough.

## Exactly one next executable action

1. Derive `ideas/artifacts/ECDLP-IDEA-358/slice_decomposition_obligations.md` as an endpoint-only theorem receipt for subset-stable exact restricted nonvanishing with every bisection query charged.
