---
id: KN-LIT-7f3c21
type: literature
title: "Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications (RFC 9106)"
authors:
  - "A. Biryukov"
  - "D. Dinu"
  - "D. Khovratovich"
  - "S. Josefsson"
year: 2021
venue: "IRTF (Crypto Forum Research Group), Informational RFC"
identifiers:
  eprint: null
  doi: "10.17487/RFC9106"
  arxiv: null
  url: "https://www.rfc-editor.org/rfc/rfc9106.txt"
  rfc_number: 9106
  alt_url: "https://datatracker.ietf.org/doc/html/rfc9106"
tags: [argon2, memory-hard, password-hashing, kdf, side-channel, rfc]
confidence: established
citation_verified: true
added: "2026-08-12"
superseded_by: null
---

## Contribution
RFC 9106 is the implementer-oriented, CFRG-consensus specification of Argon2
version 1.3 (the winner of the 2015 Password Hashing Competition), covering
the algorithm, indexing rules, compression function, recommended parameter
choices, official test vectors, and a security-considerations section with
concrete time-space trade-off attack factors. Published September 2021,
Informational status (not Standards Track).

## Key claims (as read, primary text obtained via raw HTTP fetch)

Fetch provenance: `curl -s --max-time 20 -o rfc9106.txt
https://www.rfc-editor.org/rfc/rfc9106.txt` returned HTTP 200 and the full
975-line plain-text RFC on the first attempt (route 1 of the constraint's
ordered fallback list; routes 2/3 were not needed). The full text was read
in this session, not sampled or title-only.

### Algorithm structure (Sec. 3)
- Argon2 has one primary variant, **Argon2id**, and two supplementary
  variants, **Argon2d** (data-dependent memory access; suited to
  cryptocurrency/proof-of-work, no side-channel threat model) and
  **Argon2i** (data-independent memory access; preferred for password
  hashing/KDF use, more passes needed to resist trade-off attacks).
  **Argon2id** runs Argon2i-style indexing for the first half of the first
  pass and Argon2d-style indexing for the rest, combining side-channel
  resistance with brute-force cost. Argon2id MUST be supported by any
  conforming implementation; Argon2d/Argon2i MAY be supported.
- Memory is organized as a matrix `B[i][j]` with `p` lanes (rows) and
  `q = m'/p` columns, `m' = 4*p*floor(m/4p)` blocks of 1024 bytes each.
  Each block after the first two per lane is computed as
  `B[i][j] = G(B[i][j-1], B[l][z])` -- i.e. every block has (a) a linear
  "previous block in this lane" dependency and (b) exactly one reference
  dependency on an earlier block `B[l][z]` chosen by an indexing function.
  With `t > 1` passes, later passes XOR the new computation into the old
  block value rather than overwriting it.
- Memory is further split into `SL = 4` vertical slices per pass; a slice
  x lane intersection is a "segment." Segments of the same slice compute
  in parallel (no cross-references within a slice); blocks in earlier,
  finished slices/segments are eligible reference targets.
- `H'` is the variable-length hash built from BLAKE2b; the compression
  function `G` applies BLAKE2b's round permutation `P` rowwise then
  columnwise to an 8x8 register matrix, with 64-bit multiplication added to
  `GB` (the sole deviation from vanilla BLAKE2b), specifically to increase
  ASIC circuit depth.

### Indexing (Sec. 3.4, resolves proposal.md C2-C4, C6)
- **Argon2d** (Sec. 3.4.1.1): `J_1 = int32(extract(B[i][j-1], 0))`,
  `J_2 = int32(extract(B[i][j-1], 1))` -- i.e. `J_1`/`J_2` are taken directly
  from the first 64 bits of the *content* of the immediately preceding block
  in the lane. Confirms C4 exactly.
- **Argon2i** (Sec. 3.4.1.2): `J_1`/`J_2` are derived from applying `G`
  twice to a counter `Z` built from `(pass r, lane l, slice sl, m', t, y)`
  and a running counter -- i.e. a pseudorandom stream that depends only on
  position/parameter metadata, not on password/salt *content* or on
  previously computed block values. Confirms C3 exactly (data-independent
  access pattern; the resulting reference *values* are still a function of
  H_0, which does depend on password/salt, but the *access pattern itself*
  does not depend on runtime block contents).
- **Argon2id** (Sec. 3.4.1.3): if pass number is 0 and slice number is 0 or
  1 (i.e., literally "first half of the first pass," not an approximation),
  use Argon2i-style indexing; otherwise use Argon2d-style. Confirms C5
  exactly, including the precise split point the proposal had marked as an
  imprecise recollection.
- **Reference index mapping** (Sec. 3.4.2, Figures 12-13, resolves C6): the
  within-window offset is **not** uniform over the eligible window `W`.
  Given `J_1`, compute (floating-point form) `J_1 -> |W|(1 - J_1^2/2^64)`,
  or the integer approximation actually specified:
  `x = J_1^2 / 2^32; y = (|W| * x) / 2^32; zz = |W| - 1 - y`; then take the
  `zz`-th index from `W`. This is a monotone transform of a uniform 32-bit
  value that concentrates probability toward **large `zz`, i.e. toward the
  end of `W` as constructed -- which the RFC's own text organizes so that
  recently computed / nearby blocks are favored.** This confirms the shape
  of C6's recalled formula (`z = (W-1) - W*J1^2/2^32`) essentially verbatim;
  the proposal's recalled formula was accurate.

### Recommended parameters (Sec. 4, resolves C7)
- **FIRST RECOMMENDED**: Argon2id, `t=1` iteration, `p=4` lanes,
  `m=2^21` KiB (2 GiB RAM), 128-bit salt, 256-bit tag. Suggested default for
  all environments (Sec. 7.4 repeats this as the top recommendation).
- **SECOND RECOMMENDED** (memory-constrained): Argon2id, `t=3` iterations,
  `p=4` lanes, `m=2^16` KiB (64 MiB RAM), 128-bit salt, 256-bit tag.
- Additional illustrative settings given for specific use cases: Argon2d
  with 2 lanes / 250 MiB for cryptocurrency mining (~0.1s on a 2 GHz
  1-core CPU); Argon2id with 8 lanes / 4 GiB for backend server auth
  (~0.5s, 4 cores); Argon2id with 4 lanes / 6 GiB for disk-encryption KDF
  (~3s, 2 cores); Argon2id with 4 lanes / 1 GiB for frontend server auth
  (~0.5s, 2 cores).
- An 11-step selection procedure is given (Sec. 4) for deriving custom
  `(t, m, p)` when the two RECOMMENDED defaults do not apply.

### Security considerations (Sec. 7)
- Collision/preimage resistance is that of the underlying BLAKE2b:
  `2^256` for collisions, `2^512` for preimages. KDF distinguishing
  advantage requires a minimum of `min(2^128, 2^length(K))` BLAKE2b calls.
- Time-space trade-off attack factors (reduction to the time-area product),
  as cited in the RFC from [CBS16]/[AB16]/[BZ17]:
  - 1- and 2-pass Argon2i: low-storage attack reduces time-area product by
    factor 5.
  - 3+-pass Argon2i: reduction factor is a function of memory and pass
    count (e.g., for 1 GiB: factor 3 at 3 passes, 2.5 at 4 passes, 2 at 6
    passes); grows ~0.5 per doubling of memory. To fully prevent this
    class of attack, passes MUST exceed `log2(memory) - 26`.
  - 1-pass Argon2i asymptotic bound: adversary advantage upper-bounded by
    `O(m^0.233)`, and [BZ17] proves `O(m^0.25)` is optimal for any attack --
    i.e. the RFC states 1-pass Argon2i is provably close to optimally hard
    against this attack class.
  - t-pass Argon2d: ranking trade-off attack, factor 1.33.
  - 1-pass Argon2id: combined low-storage (first half) + ranking (second
    half) attack, factor ~2.1. t-pass Argon2id: ranking attack, factor 1.33
    (same as Argon2d).
- Sec. 7.3: for time-bounded defenders, [AB16]'s cost estimates imply 3
  passes is near-optimal for Argon2i across most memory sizes, while 1 pass
  maximizes attacker cost (for fixed defender time) for Argon2d/Argon2id.

## Relevance to this program
Primary-source basis for GOAL-ARGON-001 / RQ-ARGON-141710. Directly resolves
claims C1-C7 as tabulated in
`coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/tasks/TASK-20260809-4e04eb/proposal.md`
Sec. 3 (all previously marked RECALLED, UNVERIFIED) from RECALLED to READ: C1
(linear per-lane chain) and C2 (one reference edge per block) are confirmed
by Sec. 3.2 Figure 5/6; C3 (Argon2i data-independent indexing), C4 (Argon2d
data-dependent indexing), C5 (exact Argon2id split point: pass 0, slice 0 or
1), C6 (nonuniform offset transform, formula verified near-verbatim), and C7
(recommended parameter table, both RECOMMENDED tuples plus four illustrative
settings) are confirmed by Secs. 3.4-3.4.2 and 4 respectively. This entry
files the primary text as program-cited knowledge rather than leaving the
underlying claims as ad hoc, session-local corroboration
(`coordination/goals/GOAL-ARGON-001/batches/BATCH-09d69e/reviews/TASK-20260809-28c68e/validation_report.yaml`).
No security verdict, deprecation, or recommendation about any Argon2
parameter set is asserted by this entry beyond directly reporting what
Sec. 4 and Sec. 7 of the RFC itself state; upgrading C1-C7 in the proposal
document, and any downstream hypothesis/experiment design using this entry,
is out of this task's scope (Coordinator-only follow-up).

## Not verified here
The full RFC text (Secs. 1-8, including Sec. 5 test vectors and Sec. 8
references) was read in this session. Not independently re-derived or
re-computed here: the Sec. 5 Argon2d/Argon2i/Argon2id test vectors
themselves (recorded as present, not re-executed against a reference
implementation), and the correctness of the external attack-factor citations
[CBS16]/[AB16]/[BZ17]/[AB15] beyond what RFC 9106 itself reports about them
(those are reported-by-RFC-9106 claims about other papers, not independently
checked against those papers).

## Local copies
None. Fetched directly via HTTP for this session; no local PDF/text copy was
retained under `downloads/` or elsewhere by this task (write scope limited to
this entry and the task receipt).
