# Pre-ID duplicate draft — AMS moment source sketch

## Status and claim labels

- Prospect: `20260721-c-K09`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: streaming_moment_sketch / conservative / pre-ID screen.
- State: merged_rejected_supplied_stream_and_approximate_moments.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: none.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a moment estimate or relation count is not an ECDLP result.

## Falsifiable hypothesis

Stream endpoint-derived partial-source events into Alon–Matias–Szegedy frequency-moment sketches, use exact moment signatures to detect every restricted source fibre, and decode one signed occurrence below rho and BSGS.

## Mechanism-new operation

The native operation uses randomized linear statistics to approximate frequency moments of a supplied stream in sublinear memory. It counts only if the event stream is generated without source enumeration, sketch equality gives exact empty/singleton semantics, and a positive sketch decodes an occurrence; sketching a supplied source stream is a control.

## Assumptions

1. Public endpoints generate a sub-source-sized update stream with exact relation-frequency semantics.
2. A bounded number of AMS sketches separates zero, singleton, and collision fibres with failure at most `2^-80`.
3. Restrictions update sketches without replaying the full stream.
4. A positive signature lifts to signed occurrences on all exceptional strata.
5. Frozen sketches support relation and fresh masked targets.

## Semantic fingerprint

`public_endpoint_update_stream | AMS_random_frequency_moment_sketch | exact_restricted_zero_singleton_test | sketch_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact subset-stable source return.
2. `ideas/rejected/ECDLP-IDEA-347_countsketch_heavy_endpoint_source_decoder_hypothesis.md` — heavy-hitter sketches miss rare exact sources.
3. `ideas/rejected/preallocation/20260719-d_D02_count_min_source_frequency_sketch_preid_duplicate.md` — frequency estimates consume a source stream.
4. `ideas/rejected/preallocation/20260719-d_D10_hyperloglog_source_cardinality_gate_preid_duplicate.md` — approximate cardinality does not prove emptiness or replay.
5. `ideas/rejected/preallocation/20260720-a_E01_kll_quantile_source_compactor_preid_duplicate.md` — stream compaction loses occurrence ancestry.

## Closest primary literature

- Alon, Matias, and Szegedy, [The space complexity of approximating the frequency moments](https://doi.org/10.1006/jcss.1997.1545), gives randomized approximate moments for a supplied stream.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not generate the source update stream.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source gives a source-free ECDLP stream, exact zero semantics, or occurrence decoder; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, update definition, sketch family/seeds, restrictions, charts, and verifier.
2. Generate updates from public endpoints only and audit every update for source provenance.
3. For known-log targets, make exact restricted decisions, decode/replay a labelled tuple, and verify point equality.
4. Retain all sketch failures and dependencies, collect at least `max(d_FB+32,1000)` rows, require rank `d_FB`, and solve all factor logs.
5. Freeze sketches before `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and verify `[x]P=Q`.
6. Charge stream generation, updates, repetitions, restriction rebuilds, decoding, errors, density, rank, logs, bit time, and memory.

## Full rho/BSGS cost model

Charge stream/sketch setup in `a,a_m`, restricted queries/decoding in `q,q_m`, and repetitions/ambiguity in `o,u`. With `beta=1/5`, use `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; charge failure amplification and worst-case negative queries. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, failure `<=2^-80`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

AMS sketches begin with a supplied stream and approximate aggregate moments. The elliptic source-event stream is the missing relation deck; generating it restores source traffic. Relative error is meaningless at zero and can miss singleton fibres among large background mass, while moments do not identify which signed factor occurrences contributed.

## Proof track

Give an endpoint-only update generator, an exact zero/singleton separation theorem under all restrictions, and a charged sparse occurrence decoder.

## Disproof track

Trace update origins, test zero/singleton/adversarial collisions and restricted rebuilds, and falsify on source enumeration, approximate-only moments, or missing replay.

## Positive and negative controls

- Positive: supplied turnstile streams with planted one-sparse labelled frequencies.
- Negative: zero/singleton streams under heavy background, cancellation, duplicate occurrences, empty restrictions, and fresh targets.
- Baselines: CountSketch, Count–Min, HyperLogLog, KLL, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only updates, exact semantic failure `<=2^-80`, four sizes, zero observed false decisions, exact lifts, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied stream items, a false answer, no decoder, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-c/k09_update_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-c/k09_moment_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-c/k09_cost_analysis.md`

## Interpretation boundary

This rejects the exact endpoint-source sketch transplant, not AMS streaming. Any moment estimate remains toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not run an experiment.
