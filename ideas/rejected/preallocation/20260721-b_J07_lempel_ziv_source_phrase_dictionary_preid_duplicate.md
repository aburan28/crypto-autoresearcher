# Pre-ID duplicate draft — Lempel–Ziv source phrase dictionary

## Status and claim labels

- Prospect: `20260721-b-J07`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: adaptive_dictionary_compression / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_serialization_and_no_random_access_exactness.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no dispatchable contract.
- Labels: all finite controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; lossless compression or a decoded relation is not an ECDLP result.

## Falsifiable hypothesis

Serialize the endpoint-conditioned restriction/source stream in a target-independent order, compress repeated source grammar by Lempel–Ziv phrases, and use dictionary phrase pointers to answer fresh exact restrictions and replay one signed tuple below rho and BSGS.

## Mechanism-new operation

The native operation greedily factors a supplied sequence into phrases copied from earlier text plus a new symbol. It counts only if the serialization is endpoint-derived without enumerating the source stream and compressed phrases support exact random-access restricted existence with occurrence backpointers.

## Assumptions

1. There is a public target-independent serialization whose phrase count is at most `B^(9/4+o(1))`.
2. The serialization can be generated without reading `B^3` or `B^5` source symbols.
3. Restrictions map to phrase intervals without decompressing the stream.
4. Phrase copies preserve repeated signed occurrence ancestry and empty intervals.
5. A single dictionary serves relation collection and fresh scalar-blind targets.

## Semantic fingerprint

`public_endpoint_source_serialization | Lempel_Ziv_adaptive_phrase_parse | restricted_phrase_interval_query | phrase_pointer_to_signed_occurrence | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact restriction and replay frontier.
2. `ideas/rejected/ECDLP-IDEA-371_jez_recompression_source_grammar_hypothesis.md` — grammar compression begins from source text.
3. `ideas/rejected/preallocation/20260719-d_D03_suffix_array_source_interval_index_preid_duplicate.md` — text indexes require a supplied serialization.
4. `ideas/rejected/preallocation/20260719-a_A06_fm_index_backward_source_unranking_preid_duplicate.md` — compressed indexing preserves supplied text, not hidden source generation.
5. `ideas/rejected/preallocation/20260721-a_I07_rabin_karp_endpoint_fingerprint_preid_duplicate.md` — rolling hashes begin after the source stream exists.

## Closest primary literature

- Ziv and Lempel, [A universal algorithm for sequential data compression](https://doi.org/10.1109/TIT.1977.1055714), gives adaptive lossless parsing for a supplied sequence.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), does not supply the proposed source serialization.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs or skips generation of the elliptic source stream; application novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze curve, factor base, signed decks, serialization order, restrictions, exceptional charts, dictionary rules, and verifier.
2. Generate and parse the stream from public endpoints only; retain phrase origins, lengths, random-access support, and generation costs.
3. For known-log targets, make at most `5 ceil(log_2 B)+O(1)` exact restricted queries, follow phrase pointers to one occurrence-labelled tuple, and verify point equality.
4. Collect at least `max(d_FB+32,1000)` verified rows, retain dependencies/failures, require rank `d_FB`, and solve factor logs.
5. Reuse unchanged dictionary for `Q+[t]P`, recover a tuple, compute `x=sum epsilon_i log_P(A_i)-t mod N`, and independently verify `[x]P=Q`.
6. Charge stream generation, parsing, phrase dictionary, random access, decompression, negative queries, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Charge `T_stream+T_parse` and `M_dict+M_random_access` in `a,a_m`; charge phrase lookup, decompression, and replay in `q,q_m`. For `beta=1/5`, density exponents `delta,delta_t`, rank credit `r`, output `o`, ambiguity `u`, and log costs `ell,ell_m`, charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and `mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS remain `0.50`.

## Likely fatal obstruction

Lempel–Ziv compresses only after reading the input stream. The elliptic source serialization is the missing source-bearing object, so parsing charges its full generation traffic. Phrase boundaries follow prior text rather than endpoint restrictions; exact random access and occurrence backpointers can force decompression or an index comparable to the source stream. A low phrase count does not prove fast construction.

## Proof track

Give an output-skipping endpoint phrase generator, prove restriction-stable random access and exact source ancestry, and bound construction plus all-negative queries.

## Disproof track

Instrument every emitted symbol and phrase pointer; falsify if source enumeration precedes compression, if restrictions cross many phrases, or if copied phrases merge occurrence labels.

## Positive and negative controls

- Positive: supplied repetitive labelled streams with known LZ parse and interval witnesses.
- Negative: incompressible streams, duplicate substrings with different source labels, empty intervals, adversarial query cuts, and fresh targets.
- Baselines: explicit stream scan, Jeż recompression, suffix/FM indexes, Rabin–Karp, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Promote only with endpoint-only output-skipping generation, four sizes, exact restricted queries, zero false answers, full rank, 100 fresh descents, both caps, and `lambda,mu<=0.45`. Falsify on supplied stream input, linear-in-source generation, label loss, any false answer, or exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-b/j07_stream_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-b/j07_phrase_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-b/j07_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint source-stream compiler, not Lempel–Ziv compression. Finite results remain toy, heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not construct or run an experiment.
