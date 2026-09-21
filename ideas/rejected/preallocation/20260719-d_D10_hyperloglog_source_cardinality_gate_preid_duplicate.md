# Pre-ID duplicate draft — HyperLogLog source-cardinality gate

## Status and claim labels

- Prospect: `20260719-d-D10`; no canonical ECDLP idea ID was allocated
- Class / risk / lane: `probabilistic_cardinality_sketch` / `conservative` / pre-ID screen
- State: `merged_rejected_supplied_stream_and_lost_source_identity`
- Evidence: complete ledger/corpus and primary-literature review only; no experiment ran
- Contract posture: none
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`; Breakthrough claim: **none**

## Falsifiable hypothesis

Hash endpoint-derived accepting-event identifiers into HyperLogLog registers for each dyadic fifth-label restriction. Register occupancy would separate an empty supplied stream from a nonempty one exactly, while the harmonic-mean cardinality estimate remains approximate; auxiliary provenance would replay a tuple for relations and fresh blind descent below rho and BSGS.

## Mechanism-new operation

HyperLogLog partitions hashed stream items into registers and stores leading-zero maxima to estimate distinct cardinality. An all-zero register array exactly detects an empty supplied stream, but the sketch does not generate that stream or retain item identity. It counts only if the event stream is generated endpoint-only and occurrence replay is added without restoring a source dictionary; sketching supplied sources is a control.

## Assumptions

1. Accepting source tuples emit distinct public identifiers without explicit enumeration.
2. Stream construction, hashing, register updates, small/large-range correction, restrictions, error probability, provenance, replay, rank, logs, descent, bit time, and memory are charged.
3. Empty versus nonempty stream occupancy is exact across all adaptive bisection queries, while singleton identity and exact cardinality are not inferred from the aggregate.
4. One frozen hash/register family serves known-log and fresh scalar-blind targets.
5. No exact cleanup dictionary, repeated rerun until success, post-hoc selector, dense target vector, or source-provided event stream is admitted.

## Semantic fingerprint

`endpoint_accepting_event_stream | HyperLogLog_register_maxima | exact_restricted_empty_nonempty_bit | register_provenance_to_signed_occurrence | factor_logs_and_blind_descent`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1553-ZR-R4`: exact nonemptiness, not approximate cardinality, is required.
2. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H675`: a public source-resolving circuit is missing.
3. `inputs/ledger_inventory_20260719.json` — imported `ECFG-H676`: source events cannot be assumed as the stream.
4. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1434-EXPLICIT-SOURCE-EDGE-BOUNDARY`: streamed identifiers are source records.
5. `inputs/ledger_inventory_20260719.json` — imported `ECFG-NR-1479`: aggregate public features do not complete factor logs.

## Closest primary literature

- Flajolet, Fusy, Gandouet, and Meunier, [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](https://doi.org/10.46298/dmtcs.3545), estimates distinct items in a supplied stream with nonzero statistical error.
- Alon, Matias, and Szegedy, [The space complexity of approximating the frequency moments](https://doi.org/10.1145/258533.258545), gives the streaming-approximation neighborhood, not exact source support.
- Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031) and Shoup's [generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf) set the endpoint and baseline boundaries.

## Complete factor-base-to-target-descent path

1. Freeze curve, decks, charts, event IDs, hashes, registers, restrictions, decision threshold, and verifier.
2. Build target-independent state within `B^(9/4+o(1))` without enumerating accepting events.
3. Answer exact restricted nonemptiness for known-log targets and replay five verified occurrences.
4. Collect at least `B` independent rows, preserve every uncertain/failed query, and solve factor-base logarithms.
5. Reuse unchanged state on fresh scalar-blind `Q+[t]P`, recover/verify a tuple, remove `t`, and verify `[x]P=Q`.
6. Charge stream generation, all hashes/updates, failure amplification, restrictions, provenance, rank, logs, descent, verification, bit work, and peak memory.

For explicit scalar semantics, write each recovered factor-base occurrence as `A_i=[alpha_i]P` with sign `epsilon_i in {+1,-1}`. A known-log relation target `R=[kappa]P` yields the checked row `sum_i epsilon_i alpha_i = kappa (mod N)`. Source replay uses at most `5 ceil(log_2 B)+O(1)` charged positive-parent/negative-child restriction queries plus singleton checks. For a fresh masked target `R=Q+[t]P=[x+t]P`, a verified tuple yields `x=sum_i epsilon_i log_P(A_i)-t (mod N)`; the final check is `[x]P=Q`. Every failed restriction branch and scalar verification is charged.

## Full rho/BSGS cost model

Let `a,a_m` charge endpoint-event construction, every HLL hash/register update, restriction state, and any provenance satellite; let `q,q_m` charge target-dependent restricted-stream generation, occupancy/cardinality evaluation, bisection, negative branches, and replay. Let `delta,delta_t` be reciprocal verified relation/target success after source-identity checks, `o` output, `r` verified independent-rank credit, `u` register/source ambiguity plus hash-failure amplification/rebuilds, and `ell,ell_m` factor-log time/state.

With `B=N^beta`, `beta=1/5`, require `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`, `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`, setup/state `<=B^(9/4+o(1))`, total fresh stream/register/replay work `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`. Rho time and BSGS time/memory are exponent-`0.50` controls. The complete accepting-event stream, all restriction-specific updates, and occurrence provenance are charged.

## Likely fatal obstruction

HyperLogLog consumes the source event stream and intentionally discards identities. Register occupancy does give exact emptiness after that stream is supplied, but constructing a restricted accepting-event stream is P1553 R4 and adding occurrence provenance restores an exact source dictionary. The cardinality estimate itself remains approximate. This merges with IDEAs `053/191/347/366/380`, pre-ID `B11/C11`, and D02.

## Proof track

Construct restricted events endpoint-only and prove exact nonemptiness plus source replay from the resulting registers within the caps, then close rank and blind descent.

## Disproof track

Give two nonempty event sets with identical registers but different source identities, or expose source enumeration in restricted event generation.

## Positive and negative controls

- Positive: supplied empty/nonempty streams must pass exact occupancy while larger streams reproduce the published estimator law.
- Negative: equal nonempty register arrays with different source identities, adaptive restrictions requiring new source streams, exceptional charts, and blind targets.
- Baselines: IDEAs `053/191/347/366/380`, pre-ID `B11/C11`, D02, exact bitmaps, P1553 R4, rho, BSGS.

## Quantitative promotion and falsification gates

- Promote only with endpoint-only restricted events, exact empty/nonempty occupancy and source replay, `1,000` independent rows, `100` blind descents, both caps, and `lambda,mu<=0.45`.
- Falsify on one supplied event, one register/source-identity collision without replay, target rebuild, cap violation, or complete exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260719-d/d10_event_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260719-d/d10_register_collision_controls.json`
- `ideas/rejected/preallocation/artifacts/20260719-d/d10_cost_analysis.md`

## Interpretation boundary

This rejects exact-source use of HyperLogLog, not cardinality estimation. A calibrated estimate or toy empty test is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/rejected/preallocation/artifacts/20260719-d/d10_event_provenance.md` and classify every hashed identifier and register-provenance field by endpoint/source dependence.
