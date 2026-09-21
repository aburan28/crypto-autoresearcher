# Pre-ID duplicate draft — Rabin–Karp endpoint fingerprint

## Status and claim labels

- Prospect: `20260721-a-I07`; no canonical ECDLP idea ID was allocated.
- Class / risk / lane: randomized_fingerprint / conservative / conservative pre-ID screen.
- State: merged_rejected_supplied_serialization_and_false_positive_filter.
- Evidence: complete ledger/corpus and checked primary-literature review only; no experiment ran.
- Contract posture: no executable contract.
- Labels: controls are toy; extrapolations are heuristic, model-bound, and novelty-unverified.
- Breakthrough claim: none; a fingerprint match, verified relation, or toy scalar is not a breakthrough.

## Falsifiable hypothesis

Serialize endpoint-derived partial source states so rolling Rabin–Karp fingerprints locate exact compatible windows, after which labelled signed sources, factor logs, and blind targets are recovered below rho/BSGS.

## Mechanism-new operation

Rabin–Karp updates a short modular fingerprint for consecutive windows of a supplied text and verifies hash matches. It counts only if the text/order is public-endpoint-derived before source incidence, compatible sources form searchable windows, and every match replays all occurrences; hashing a source serialization is a control.

## Assumptions

1. A target-independent endpoint serialization contains every valid tuple contiguously without enumerating it.
2. Restrictions map to fingerprint patterns with sub-source traffic.
3. Hash moduli/seeds, collision probability, verification, and adversarial targets are charged.
4. Duplicate, signed, exceptional, and empty cases retain exact backpointers.
5. The same serialized state serves relations and blind descent.

## Semantic fingerprint

`public_endpoint_serialization | Rabin_Karp_rolling_modular_fingerprint | exact_restricted_window_match | verified_window_to_signed_occurrences | logs_and_blind_descent`

## Five closest ledger entries

1. `ideas/rejected/preallocation/20260719-a_A11_fks_perfect_hash_source_dictionary_preid_duplicate.md` — exact hashes require a supplied source key set.
2. `ideas/rejected/preallocation/20260720-b_F09_kmp_failure_link_source_matcher_preid_duplicate.md` — pattern matching starts from supplied text.
3. `ideas/rejected/preallocation/20260720-c_G08_boyer_moore_source_skip_preid_duplicate.md` — skipping changes search backend only.
4. `ideas/rejected/preallocation/20260720-d_H01_patricia_radix_source_trie_preid_duplicate.md` — compressed keys do not create target-dependent bits.
5. `ideas/rejected/preallocation/20260720-a_E10_merkle_source_commitment_tree_preid_duplicate.md` — fingerprints/commitments certify supplied data but do not find sources.

## Closest primary literature

- Karp and Rabin, [Efficient randomized pattern-matching algorithms](https://doi.org/10.1147/rd.312.0249), fingerprints windows of a supplied text and verifies collisions.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies endpoint equations, not a source text.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic baseline.

No checked source constructs this endpoint serialization; novelty is unverified.

## Complete factor-base-to-target-descent path

1. Freeze the curve, factor base, serialization/order, fingerprint family, restrictions, signed strata, and verifier.
2. Build the text/fingerprint state from public endpoints without enumerating source tuples or calling `Query2P1`.
3. For each known-log target, issue restricted fingerprint searches, verify every candidate, replay labelled points, verify the point sum, and record valid rows.
4. Retain collisions/misses/dependencies; collect at least `max(d_FB+32,1000)` verified rows for actual `d_FB`, require rank `d_FB`, and solve logs.
5. Reuse unchanged state for `Q+[t]P`, replay, compute `x`, and verify `[x]P=Q`.
6. Charge serialization, hashes, scans, seeds, collision verification, restrictions, replay, density, rank, logs, descent, bit time, and memory.

## Full rho/BSGS cost model

Let `a,a_m` charge serialization/fingerprint setup and `q,q_m` charge all scanned windows, collision checks, restrictions, and replay. With `B=N^(1/5)`, charge

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`, `beta=1/5`, `0<=r<=o`.

Collision amplification is in `u`. Require setup/state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`, and `lambda,mu<=0.45`; rho/BSGS are `0.50`.

## Likely fatal obstruction

Rolling fingerprints accelerate matching only after a text and window order exist. No endpoint-only ordering makes all compatible five-tuples contiguous; serializing them materializes source state. Hash verification filters false positives but creates neither the missing windows nor restriction-stable occurrence replay.

## Proof track

Derive an endpoint-only compact serialization with a contiguity theorem, exact all-occurrence backpointers, recorded collision bounds, and complete sub-rho costs.

## Disproof track

Audit text symbols and window boundaries; falsify if any comes from source enumeration, compatible tuples are noncontiguous, or collision/scan traffic reaches the source deck.

## Positive and negative controls

- Positive: supplied texts with planted repeated patterns and exact occurrence lists.
- Negative: adversarial hash collisions, noncontiguous tuple encodings, duplicate windows, shuffled backpointers, empty restrictions, and blind targets.
- Baselines: KMP/Boyer–Moore/FKS/PATRICIA, explicit scanning, P1553 R4, rho, and BSGS.

## Quantitative promotion and falsification gates

Require an endpoint-only contiguity proof, failure at most `2^-80`, zero missed occurrences, exact lifts, four increasing sizes, rank `d_FB` from `max(d_FB+32,1000)` rows, 100 blind descents, both caps, and 95% upper bounds `lambda,mu<=0.45`. Falsify on supplied text, missed/noncontiguous witness, collision overload, cap failure, or complete exponent at least `0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260721-a/i07_serialization_origin_audit.md`
- `ideas/rejected/preallocation/artifacts/20260721-a/i07_fingerprint_controls.json`
- `ideas/rejected/preallocation/artifacts/20260721-a/i07_cost_analysis.md`

## Interpretation boundary

This rejects the endpoint serialization, not Rabin–Karp. Toy matches remain heuristic, model-bound, novelty-unverified, and not a breakthrough.

## Exactly one next executable action

1. Submit this frozen record to an independent `review-xhigh` Red Team; do not build the serialized source text.
