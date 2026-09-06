# TASK-20260825-3da758 modern-hash frontier shard

## Outcome

The shard contains 27 primary-source-backed rows covering reduced-round SHA-256/SHA-512, all six FIPS 202 SHA-3/SHAKE instances, Keccak-p[1600] permutation distinguishers, BLAKE2/BLAKE3 internal components, and the standardized Ascon-Hash256/Ascon-XOF128 constructions. Every manifest primitive has a terminal `primary_source_partial` coverage state. No blank notion cell is described as secure.

Rows by provenance and eligibility:

- `retrieved`: 27
- `author_reported_primary_text_read`: 27
- `is_frontier: true`: 24 author-reported candidates inside exact comparison keys
- `is_frontier: false`: 3 SHA-2 round-record rows whose accessible 2026 primary abstracts omit full cost vectors
- `recalled`, `secondary_pointer_only`, or `recalled_pointer_only`: 0 authoritative rows

The 24 candidates are not a cross-notion ranking. Each candidate is local to its full comparison key, including target component, output/digest parameters, attacker model, and round convention.

## Frontier candidates transcribed

- SHA-3/SHAKE collision boundary: SHA3-224/256 and SHAKE128 at five rounds (`2^96.67` source complexity), SHA3-384 at five rounds (`2^170.73`), SHA3-512 at four rounds (`2^225.29`), and fixed-output SHAKE256 at six rounds (`2^232.29`).
- SHA-3/SHAKE preimage boundary: five rounds for SHAKE128 (`2^100.5` Keccak computations), SHA3-224 (`2^216.03` bit operations), SHA3-256/SHAKE256 (`2^254.33` bit operations); four rounds for SHA3-384 (`2^277.8` source complexity); three rounds for SHA3-512 (`2^504.2`).
- Keccak-p[1600] permutation-only SymSum_Sim distinguishers: 15 rounds at `2^256` and 16 rounds at `2^512`.
- BLAKE internal components: BLAKE2s eight-round keyed-permutation boomerang at `2^182`, BLAKE2b 8.5-round keyed-permutation boomerang at `2^474`, full seven-round BLAKE3 keyed-permutation boomerang at `2^180`, and a full-round BLAKE2s chosen-IV compression collision at `2^64`.
- Standardized Ascon-Hash256: two-round collision `2^61.79`; three-round collision `2^114.13` time / `2^112` memory; three-round preimage `2^160.75` time / `2^160` memory.
- Standardized Ascon-XOF128 special models: one-round arbitrary-output second preimage `2^64` Gaussian eliminations; one-round `n`-bit preimage `2^64 + 2^(n-128)` for `n <= 255`; one-round random-prefix preimage `2^29.7` Gaussian eliminations.

## Anti-laundering checks

No anti-laundering failure was found in the written rows.

- The 15/16-round Keccak-p rows target the permutation and are never called SHA-3/SHAKE collisions or preimages.
- BLAKE2/BLAKE3 boomerang rows target keyed permutations. They are not hash-construction breaks and are not key recovery.
- The BLAKE2s `2^64` result is explicitly a fully chosen-IV compression-function collision, not a standard hash collision.
- Ascon SFS trail weight 250 is kept in source metadata only; it is not converted into an end-to-end attack exponent.
- SHA-2 free-start conversions mentioned by the source are not laundered into standard collisions.
- Fixed SHAKE output lengths are included in comparison keys. Variable-output rows are not allowed to dominate fixed-output rows.
- Reduced-round and full-round-component labels are explicit. `full_round_component` never means a full hash construction is broken.
- No practical claim was converted to `2^N` without a source-reported operation count. Time-only rows retain explicit null data/memory/preprocessing/success axes.
- Classical rows only; no quantum row participates in dominance.

## Named unresolved primary-source gaps

1. **SHA-256 37-step collision (ePrint 2026/232):** the primary HTML establishes the first 37-step attack, but the accessible text omits time, data, memory, success, and exact message-block/padding conditions. The row is therefore not placed on the frontier.
2. **SHA-256 47-step and SHA-512 51-step preimages (ePrint 2026/353):** primary HTML establishes the round records but not the complete charged cost vectors or exact initialization/message-length model. Both rows remain non-frontier.
3. **SHA-224 and SHA-384:** no construction-specific authoritative row was transcribed in the bounded search. No transfer from SHA-256/SHA-512 is inferred.
4. **SHA-512 collision update:** a 2025 31-step improvement was discovered through conference/institutional pointers, but a sufficiently exact primary-text cost/data/memory transcription was not completed in this shard.
5. **SHA-3/SHAKE cost axes:** the primary attack tables supply time/complexity values, but often omit independent data, memory, preprocessing, and success axes. Those remain explicit nulls rather than hidden assumptions.
6. **Keccak-p query/advantage axes:** the SymSum primary abstract gives overall complexities and qualitative frontier claims but the query and exact advantage conventions were not separately transcribed.
7. **BLAKE2b recency:** ePrint 2014/1012 is the located primary row for the exact 8.5-round keyed-permutation key; no exhaustive later-primary-source dominance audit was completed.
8. **BLAKE2/BLAKE3 standard hash construction:** no primary-source-backed standard collision/preimage break was transcribed. Internal-component results must remain quarantined from construction security.
9. **Ascon-Hash256 SFS collisions:** the 2025 paper reports practical three-/four-round SFS attacks and a four-round trail weight of 250, but the accessible abstract does not expose a complete end-to-end cost vector for those attacks; no attack row was synthesized from trail weight.
10. **Ascon-XOF128 ordinary multi-round preimages:** the SAC 2025 Table 1 lists prior results, but those are secondary citations within that primary paper. They were not promoted without reading each underlying primary source.
11. **Repository knowledge search:** read-only AST search returned no matches, but it may not index every Markdown/PDF corpus asset; the result is recorded as a boundary, not evidence of absence.

## Coverage boundary

This is a bounded acquisition shard, not a claim that the global modern-hash literature is complete. Every primitive remains `primary_source_partial`; later-batch quantum, side-channel, fault, and unlisted primitive work is outside the frozen scope. The shard supplies frontier lines that can be reviewed and extended without erasing unresolved cells or confusing construction, compression-function, and permutation security.
