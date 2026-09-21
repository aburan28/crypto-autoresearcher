# ECDLP-IDEA-347 — CountSketch heavy-endpoint source decoder

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_sketch_stream_requires_tuple_enumeration_and_sources_are_not_heavy`
- Cohort: `20260718-p`
- Evidence scale: exhaustive semantic, cost, and primary-literature audit only; no experiment ran
- Contract posture: `none`
- Scale labels: every prospective finite check is `toy`; every extrapolation is `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a recovered heavy bucket or valid relation is not an ECDLP break.

## Falsifiable hypothesis

A public signed stream of partial-sum contributions can be sketched without enumerating its source tuples, and valid relation endpoints become heavy enough that a hierarchical CountSketch decoder returns every exact source tuple within the P1553 bounds.

## Mechanism-new operation

The screened operation is **apply signed hash-bucket sketches to an implicit endpoint-contribution stream, identify heavy endpoint buckets, and recursively decode exact source tuples**. It is distinct only if the stream updates are generated without listing the contributing tuples and if exact relation sources, rather than merely frequent endpoints, are decoded. Otherwise it is a hashed table or source-labelled accumulator control.

## Assumptions

1. Every sketch update is produced from public curve data without enumerating the source tuple deck.
2. Relation-bearing endpoints satisfy an explicit heavy-hitter gap under every required signed and overlap stratum.
3. Hash collisions, cancellation, false positives, and low-frequency valid sources are recovered exactly.
4. The decoder returns replayable factor-base tuples, not bucket identifiers or aggregate counts.
5. Stream generation, repetitions, decoding, output, rank, logs, blind descent, and memory are charged.

## Semantic fingerprint

`signed_tuple_contribution_stream | CountSketch_hash_buckets | heavy_endpoint_detection | hierarchical_exact_source_decode | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source-fibre generator.
2. `inputs/ledger_inventory.json` — imported `ECFG-H662`, the source-faithful endpoint-reporting obligation.
3. `inputs/ledger_inventory.json` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`, where an aggregate linear representation does not supply sources.
4. `inputs/ledger_inventory.json` — imported `ECFG-NR-1427-ROW-GCD-ZERO-OUTPUT-NO-PROMOTION`, where a zero aggregate output does not report a relation row.
5. `inputs/ledger_inventory.json` — imported `ECFG-H674`, the witness extraction and nonlinear-composition requirement.

## Closest primary literature

- Charikar, Chen, and Farach-Colton, [Finding frequent items in data streams](https://doi.org/10.1016/S0304-3975(03)00400-6), gives CountSketch guarantees for an explicit update stream and frequency-heavy coordinates; it does not construct hidden elliptic source updates.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies an endpoint equation rather than a heavy-hitter stream or exact source decoder.

No checked source supplies the implicit updates and exact-source gap; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, signed update rule, hash families, repetitions, decoder, and verifier.
2. Generate sketches for known-log relation collection without enumerating candidate tuples.
3. Decode heavy endpoints, recursively recover every exact tuple, replay it, and verify each relation.
4. Collect at least `B` independent rows, solve factor logs, and verify them.
5. Build the identical sketches for fresh scalar-blind masked targets.
6. Decode target tuples, substitute logs, remove masks, preserve ambiguity, and verify `[x]P=Q`.
7. Charge update generation, hash repetitions, decoding, output, rank, logs, descent, verification, and memory.

## Full rho/BSGS cost model

For `B=N^beta`, `beta=1/5`, setup `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, sketch query excluding output `N^q,N^q_m`, verified rank `N^r`, output `N^o`, ambiguity `N^u`, and factor logs `N^ell,N^ell_m`, use

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Every implicit update, counter, repetition, collision candidate, decoded tuple, and bit is charged; `0<=r<=o`. Pollard rho has expected time exponent `0.50` and negligible memory; BSGS has time and memory exponent `0.50`. Promotion requires complete exponents at most `0.45`.

## Likely fatal obstruction

CountSketch begins with a supplied update stream and recovers heavy coordinates, not the hidden contributors to one coordinate. In a target query the endpoint coordinate is already known, so declaring it heavy is vacuous and does not reveal any factor tuple. Generating a source-labelled update stream appears to enumerate the tuples the sketch was meant to avoid; relation sources are individually rare, while aggregating them at the known endpoint loses provenance. Exact hierarchical recursion or source-labelled counters restore the source deck and its cost.

## Proof track

Construct a source-free update oracle, define every level of a hierarchical contributor recursion, prove an all-strata separation for source prefixes rather than the already-known endpoint, give an exact decoder with bounded repetitions, and derive complete `lambda,mu<=0.45`.

## Disproof track

Reduce one update to tuple enumeration, exhibit a valid low-frequency source or cancelling bucket, show exact decoding needs source-labelled counters, or derive exponent at least `0.50`.

## Positive and negative controls

- Positive: explicit sparse streams with planted heavy coordinates must recover coordinates and their supplied source labels exactly.
- Negative: streams with equal endpoint frequencies but permuted source tuples, cancelling signed updates, and singleton valid sources must not invent provenance.
- Baselines: hashed meet-in-the-middle tables, source-labelled accumulators, P1553 determinant contractions, rho, and BSGS.

## Quantitative promotion and falsification gates

- Promote only with a proved update oracle, exact all-strata source recall, zero false provenance, 1,000 ranked rows, 100 blind descents, setup/state at most `B^(9/4)`, query at most `B^(5/4)`, and complete exponents at most `0.45`.
- Falsify on one update requiring source enumeration, one missed valid source, one false source, source-sized counters, or either exponent at least `0.50`.
- Heavy-bucket recovery or relation validity alone is a control and cannot promote.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-347/update_oracle_spec.md`
- `ideas/artifacts/ECDLP-IDEA-347/heavy_gap_fixtures.json`
- `ideas/artifacts/ECDLP-IDEA-347/source_replay_receipt.json`
- `ideas/artifacts/ECDLP-IDEA-347/cost_analysis.md`

## Interpretation boundary

This rejects the proposed hidden-stream decoder, not CountSketch. Every finite check would be toy, heuristic, model-bound, and novelty-unverified. A correct sketch or valid relation is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-347/update_oracle_spec.md` and account for the production of every signed update before any sketch counter is touched.
