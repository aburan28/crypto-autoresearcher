# ECDLP-IDEA-344 — Locality-sensitive exact-complement filter

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_lsh_preserves_near_neighbors_not_exact_hidden_complements`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; approximate-neighbor filtering or a hash collision is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent public embedding of pair-bivectors or partial elliptic sums into a metric in which exact complementary sources collide with locality-sensitive probability high enough, and false positives low enough, to meet the complete campaign and fresh-target bounds with exact replay.

## Mechanism-new operation

The screened operation is **embed partial source sums into a metric, use locality-sensitive filters to route likely exact complements, then verify and replay the labelled factors**. It differs from a hash table only if elliptic equality has a public geometric locality gap. Without such a theorem it is the birthday/bucket backend of IDEAs 051, 057, 134, 196, 244, and 326.

## Assumptions

1. The embedding is public, target-independent, and does not use hidden scalar coordinates or learned successful targets.
2. Exact complements are near with a provable gap from noncomplements on generic curves.
3. Pair construction, tables, probes, false positives, verification, and source output fit the frozen bounds.
4. All repeated, signed, infinity, overlap, and ambiguous strata retain exact labels.
5. The same filter works for fresh scalar-blind masked targets and full factor-log descent.

## Semantic fingerprint

`partial_elliptic_sum_embedding | public_exact_complement_locality_gap | locality_sensitive_filter_buckets | verified_labelled_source_replay | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1475`, the residual-character bucket control.
2. `inputs/ledger_inventory.json` — imported `ECFG-NR-1474`, where stable-deck transitions do not compress.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1471`, where coordinate-matched occupancy is hash-like.
4. `inputs/ledger_inventory.json` — imported `P1472`, the exact two-large-prime occupancy exponent boundary.
5. `inputs/ledger_inventory.json` — imported `P1476`, the complete m-ary support/query gate.

## Closest primary literature

- Indyk and Motwani, [Approximate nearest neighbors: towards removing the curse of dimensionality](https://doi.org/10.1145/276698.276876), indexes a supplied metric data set for approximate neighbors; it does not create an elliptic metric gap or exact witnesses.
- Charikar, Chen, and Farach-Colton, [Finding frequent items in data streams](https://doi.org/10.1016/S0304-3975(03)00400-6), is the signed-hash/sketch control and similarly begins from an explicit stream.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies exact endpoint equations rather than a locality gap.

No checked source constructs the required embedding and exact inverse; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, decks, pair representation, embedding, hash/filter family, masks, and verifier.
2. Build target-independent pair filters without scalar coordinates or post-hoc target selection.
3. Query known-log endpoints, verify every candidate complement, and replay exact signed factor points.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Query the identical structure on fresh scalar-blind masked targets and retain all false positives and misses.
6. Substitute logs, remove masks, preserve ambiguity, and verify `[x]P=Q`.
7. Charge pairs, tables, probes, repetitions, verification, output, rank, logs, descent, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, filter query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every embedded pair, hash table, repetition, false positive, and verification is charged; `0<=r<=o`. With `n=B^2` pair objects and asymmetric LSH exponents `rho_u,rho_q`, the frozen gates require `2(1+rho_u)<=9/4` for setup and `2*rho_q<=5/4` for fresh query before candidate, output, and source-replay costs. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`. Promotion requires complete exponents at most `0.45`.

## Likely fatal obstruction

Generic prime-order elliptic sums are pseudorandom in public coordinates. Exact equality is already distance zero and hash-joinable; LSH helps only if a public metric gives true complements a gap over noncomplements. No such target-independent low-distortion gap is known, so approximate neighborhoods add hash-like false positives. A one-time `B^2` pair table is inside the setup cap, but it does not by itself meet the `B^(5/4)` fresh-query, candidate-output, source-replay, and complete campaign gates; making the gap scalar-coordinate based is the DLP.

## Proof track

Prove an explicit algebraic metric gap on held-out generic curves, bound table/probe/output costs, retain all sources, and establish complete `lambda,mu<=0.45` including blind descent.

## Disproof track

Match collision probabilities to random embeddings, exhibit far/near inversions, show the metric uses scalar labels, violate `2(1+rho_u)<=9/4` or `2*rho_q<=5/4` after false-positive and output costs, or derive a complete exponent at least `0.50`.

## Positive and negative controls

- Positive: known-coordinate groups with planted metric-separated complements must route correctly.
- Negative: random embeddings, relabelled decks, and approximate near-but-not-equal pairs must not be accepted.
- Baselines: IDEAs 051/057/134/196/244/326, exact hash joins, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a proved public gap, zero accepted false sources, 1,000 ranked rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify if exact/nonexact collision probabilities are asymptotically equal, scalar labels enter, one stratum is lost, or either exponent reaches `0.50`.
- Approximate-neighbor speed on supplied pairs is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-344/embedding_definition.md`
- `ideas/artifacts/ECDLP-IDEA-344/locality_gap_obligations.md`
- `ideas/artifacts/ECDLP-IDEA-344/false_positive_controls.json`
- `ideas/artifacts/ECDLP-IDEA-344/cost_analysis.md`

## Interpretation boundary

This rejects the proposed elliptic locality gap, not locality-sensitive hashing. All finite evidence would be toy, heuristic, model-bound, and novelty-unverified. A hash collision or fast approximate query is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-344/embedding_definition.md` giving a public formula for the embedding and proving whether exact complement equality creates any target-independent distance gap.
