---
id: KN-LIT-8eb8af
type: literature
title: "Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications (RFC 9106)"
authors:
  - "Alex Biryukov"
  - "Daniel Dinu"
  - "Dmitry Khovratovich"
  - "Simon Josefsson"
year: 2021
venue: "IRTF, Crypto Forum Research Group (CFRG) — RFC 9106, ISSN 2070-1721"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  rfc: "RFC 9106"
  url: "https://www.rfc-editor.org/rfc/rfc9106.txt"
tags: [argon2, memory-hard-function, password-hashing, kdf, proof-of-work, blake2b, rfc, standards, dag, pebbling]
confidence: established
citation_verified: read
added: "2026-08-10"
superseded_by: null
---

## Contribution
Informational IRTF/CFRG specification (September 2021, corresponds to Argon2
version 1.3) giving an implementer-oriented description of the Argon2
memory-hard function family with test vectors. Argon2 has one primary
variant, **Argon2id** (MUST be supported by any implementation of the
document), and two supplementary variants, **Argon2d** (data-dependent
memory access — suitable for cryptocurrency/proof-of-work, no side-channel
timing threat model) and **Argon2i** (data-independent memory access —
preferred for password hashing / password-based key derivation). Argon2id
runs as Argon2i for the first half of the first pass over memory and as
Argon2d for the rest, combining side-channel protection with brute-force
cost from time-memory trade-offs; Argon2i compensates with more passes over
memory to resist trade-off attacks.

Argon2 is a mode of operation over a fixed-input-length compression
function G and a variable-input-length hash function H (BLAKE2b is used
throughout this document). Memory is organized as a matrix `B[i][j]` with
`p` rows (lanes, i = 0..p-1) and `q = m'/p` columns, further split into
`SL = 4` vertical slices; a slice x lane intersection is a "segment."
Segments of the same slice can be computed in parallel; blocks are computed
`B[i][j] = G(B[i][j-1], B[l][z])` where `[l][z]` is a reference block index
determined by the indexing rule below, and passes beyond the first XOR the
new value into the old (Section 3.2, Figures 1–8).

## Section 3.4 — Indexing (verbatim structure, as read from the primary text)

**3.4.1 Computing the 32-bit values J1 and J2** — used to derive the
reference-block coordinates `[l][z]` for `B[i][j] = G(B[i][j-1], B[l][z])`:

- **3.4.1.1 Argon2d**: J1 and J2 are read directly out of the *previous*
  block in the same lane, `B[i][j-1]` — i.e. block-content-dependent
  ("data-dependent") indexing:
  ```
  J1 = int32(extract(B[i][j-1], 0))
  J2 = int32(extract(B[i][j-1], 1))
  ```

- **3.4.1.2 Argon2i**: J1, J2 are derived *independently of any data block
  content* ("data-independent" indexing), from a counter-driven expansion
  of a per-segment value `Z = (LE64(r) || LE64(l) || LE64(sl) || LE64(m')
  || LE64(t) || LE64(y))` (r = pass number, l = lane number, sl = slice
  number, m' = total memory blocks, t = total passes, y = Argon2 type: 0
  Argon2d / 1 Argon2i / 2 Argon2id). For a whole segment, `q/(128*SL)`
  1024-byte values are generated as
  `G(ZERO(1024), G(ZERO(1024), Z || LE64(counter) || ZERO(968)))` for
  counter = 1, 2, ..., and partitioned into `q/SL` 8-byte values `X = X1 ||
  X2`, giving `J1 = int32(X1)`, `J2 = int32(X2)` per position in the
  segment — computed once per segment, ahead of time, not from the memory
  contents being written.

- **3.4.1.3 Argon2id**: if pass number is 0 and slice number is 0 or 1,
  compute J1/J2 as for Argon2i (data-independent); otherwise compute as for
  Argon2d (data-dependent). This is the exact mechanism by which Argon2id
  is data-independent for the first half of the first pass and
  data-dependent thereafter.

**3.4.2 Mapping J1 and J2 to reference block index [l][z]**:
`l = J2 mod p` selects the lane (for pass r=0, slice sl=0, the block is
always taken from the current lane). A candidate set `W` of already-computed,
finished block indices is assembled: if `l` is the current lane, `W`
includes all blocks in the last `SL-1 = 3` finished segments plus blocks
already computed in the current segment/pass (excluding `B[i][j-1]`); if
`l` is a different lane, `W` includes all blocks in that lane's last 3
finished segments (with the very last index excluded if `B[i][j]` is the
first block of a segment). `z` is then selected from `W` with a
**non-uniform distribution biased toward more-recently-computed blocks**
via `J1 -> |W|(1 - J1^2/2^64)`, approximated in integer arithmetic as
`x = J1^2/2^32; y = (|W|*x)/2^32; zz = |W|-1-y`, then the `zz`-th index of
`W` is used as `z`.

This non-uniform, recency-biased reference distribution (shared by all
three variants) plus the data-dependent-vs-data-independent split above is
the structural detail relevant to depth/pebbling analyses of the induced
memory-access DAG (see e.g. the cited Blocki–Zhou TCC 2017 depth-robustness
reference below, which this document itself cites in Section 7.2).

## Section 4 — Parameter Choice (recommended settings, as read from the primary text)

Named example use cases the document gives (Section 4, illustrative, not
exhaustive):
- Cryptocurrency mining, ~0.1 s on a 2 GHz CPU / 1 core — Argon2d, 2 lanes,
  250 MB RAM.
- Backend server authentication, ~0.5 s on a 2 GHz CPU / 4 cores — Argon2id,
  8 lanes, 4 GiB RAM.
- Key derivation for hard-drive encryption, ~3 s on a 2 GHz CPU / 2 cores —
  Argon2id, 4 lanes, 6 GiB RAM.
- Frontend server authentication, ~0.5 s on a 2 GHz CPU / 2 cores —
  Argon2id, 4 lanes, 1 GiB RAM.

**The two RECOMMENDED default options** (Section 4, numbered procedure
step 1–2):

| Rank | Type | Passes (t) | Lanes (p) | Memory (m) | Salt | Tag |
|---|---|---|---|---|---|---|
| FIRST RECOMMENDED | Argon2id | t = 1 | p = 4 | m = 2^21 KiB (2 GiB RAM) | 128-bit | 256-bit |
| SECOND RECOMMENDED (memory-constrained) | Argon2id | t = 3 | p = 4 | m = 2^16 KiB (64 MiB RAM) | 128-bit | 256-bit |

The 11-step selection procedure (Section 4, steps 1–11) is: (1) use the
FIRST RECOMMENDED default if a uniformly safe, application-agnostic option
suffices; (2) else use the SECOND RECOMMENDED default under tight memory;
(3) else choose the type y (Argon2id if side-channel risk is a concern or
uncertain); (4) select p = 4 lanes; (5) fix memory budget m; (6) fix time
budget; (7) select salt length (128 bits sufficient generally, 64 bits
under space constraints); (8) select tag length (128 bits sufficient for
most uses including KDF); (9) enable memory-wiping if side-channel risk is
plausible; (10) with type/m/p fixed, find the maximum t whose running time
stays within the time budget, reducing m if even t=1 exceeds it; (11) run
with the resulting (m, p, t).

## Security Considerations (Section 7, reported for citation completeness — not restated as this program's claim)

The document itself reports (its own text, not this program's assessment):
collision/preimage resistance derive from the underlying BLAKE2b (2^256 for
collision, 2^512 for preimage); KDF distinguishing security needs a minimum
of (2^128, 2^length(K)) BLAKE2b calls. On time-space trade-off resistance
(Section 7.2, citing external results): the best known attack on 1- and
2-pass Argon2i is a low-storage attack reducing the time-area product by a
factor of 5 [CBS16]; for Argon2i with ≥3 passes the reduction factor
depends on memory size and pass count (document's own worked example: for
1 GiB memory, factor 3 at 3 passes, 2.5 at 4 passes, 2 at 6 passes,
growing ~0.5 per memory doubling) [AB16]; to fully prevent this class of
trade-off the document states passes MUST exceed log2(memory) − 26;
asymptotically the best 1-pass Argon2i attack is bounded by O(m^0.233),
matching (up to the exponent) the general O(m^0.25) upper bound [BZ17].
Argon2d's best reported trade-off (ranking attack) reduces the time-area
product by a factor of 1.33; Argon2id's 1-pass trade-off factor is ~2.1
(combined low-storage + ranking attacks) and its multi-pass factor is the
same 1.33 as Argon2d. Section 7.4 states the FIRST/SECOND RECOMMENDED
Argon2id settings above as the document's own security recommendation. This
program makes no independent security assessment of Argon2/Argon2i/
Argon2d/Argon2id; the above is a relay of the RFC's stated claims for
citation purposes only.

## Normative/informative references cited by RFC 9106 relevant to this program
- [BZ17] Blocki, J. and S. Zhou, "On the Depth-Robustness and Cumulative
  Pebbling Cost of Argon2i", TCC 2017, DOI 10.1007/978-3-319-70500-2_15 —
  directly on point for depth-robustness of the Argon2i DAG; the RFC cites
  its O(m^0.233) advantage bound and its matching O(m^0.25) upper bound
  proof.
- [AB16] Alwen, J. and J. Blocki, "Efficiently Computing Data-Independent
  Memory-Hard Functions", CRYPTO 2016, DOI 10.1007/978-3-662-53008-5_9 —
  source of the pass-count-vs-memory trade-off reduction factors cited
  above and the `t > log2(m) - 26` guidance.
- [AB15] Biryukov, A. and D. Khovratovich, "Tradeoff Cryptanalysis of
  Memory-Hard Functions", ASIACRYPT 2015 — already in this corpus as
  KN-LIT-7247 (upgrade candidate: that entry is currently `confidence:
  reported` from an abstract-only pass; this RFC's Section 7.2 citation
  does not itself upgrade it, since this task did not independently
  re-verify that paper's full text).
- [HARD] Alwen, J. and V. Serbinenko, "High Parallel Complexity Graphs and
  Memory-Hard Functions", STOC '15 — general memory-hard-function/DAG
  background the RFC's Introduction cites for the "memory-hard function"
  definition.
- [ARGON2] / [ARGON2ESP] — the original Argon2 design papers (Biryukov,
  Dinu, Khovratovich), ASIACRYPT/EuroS&P antecedents of this RFC.

## Relevance to this program
This is the primary standards-track description of Argon2's indexing
function and recommended parameters, the sourcing precondition named by
`ledger/decisions/DEC-20260810-627dd4.yaml` and blocking
`TASK-20260809-4e04eb`'s proposal (RQ-ARGON-141710) and its siblings for
memory-access DAG depth-robustness measurement work. In particular it fixes
(a) the exact segment/slice/lane partition and the data-dependent vs.
data-independent J1/J2 derivation per variant (Section 3.4, transcribed
above), which is the structural input any DAG-depth or pebbling-cost
measurement needs to reproduce the correct graph, and (b) the RFC's own
recommended (t, m, p) operating points (Section 4), which are the natural
default parameterizations to measure at. No claim about Argon2's security
is made or implied by this entry; Section 7's content above is relayed
verbatim-in-substance from the RFC's own text for citation completeness
only, per this program's rule against asserting security claims in a
literature entry.

## Verification note
Fetched directly via `curl` (raw HTTP, not the WebFetch/WebSearch tools,
which failed identically for every prior agent that tried them on this
branch with an unrelated backend-model infrastructure error — see
`coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/reviews/TASK-20260809-28c68e/validation_report.yaml`
for the precedent). `https://www.rfc-editor.org/rfc/rfc9106.txt` returned
HTTP 200, 37228 bytes, on the first attempt; full log at
`coordination/goals/GOAL-ARGON-001/batches/BATCH-6286dc/tasks/TASK-20260810-921fef/fetch_log.md`.
The entire document (976 lines: Abstract through Authors' Addresses,
including Sections 3.4, 4, 5's test-vector structure, and 7) was read
directly from the fetched text by this task, not reconstructed from memory
or relayed from the prior Validator's 7-claim spot-check table.
