---
id: KN-LIT-84b674
type: literature
title: "Classic McEliece: conservative code-based cryptography: cryptosystem specification"
authors: []
authors_note: >-
  The document's title page carries no author list; it is issued by the Classic
  McEliece team. Authors are NOT filled in from recall. The team roster is at
  https://classic.mceliece.org/people.html, which no task of this program has
  fetched.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-spec-20221023.pdf"
  sha256: "dcc6878852ef8a00a7bedd859da661770cf85d2c3d9239e06d25e4a0d365fd12"
tags: [code-based, mceliece, goppa, niederreiter, specification, parameters, kem, primary-source]
confidence: reported
citation_verified: web
citation_verified_note: >-
  NOT `read`, deliberately. This document was retrieved and read by
  TASK-20260803-f3aece (BATCH-001) on 2026-08-03 — HTTP 200, 249199 bytes,
  sha256 dcc68788…, 16 pages, `source_access_log.yaml` seq 5 — and that task
  re-fetched it after writing and reproduced the hash byte-identically. But
  TASK-20260808-f9374d, which files this entry, performed NO retrieval and read
  no PDF, and the read it relies on happened in a different session on a
  different host and branch. Per RQ-MCE-e65b3c's inherited caution from
  KN-OPEN-3f7a21, a `read` this task cannot attest is not claimed. UPGRADE PATH,
  concrete: re-fetch the URL, compare against the sha256 above, and transcribe
  under the settled convention (TASK-20260808-a9f648) — which is exactly what
  TASK-20260808-1985f1 did for the companion document KN-LIT-6da230, the one
  entry of this family that does carry `read`.
added: "2026-08-08"
superseded_by: null
---

## Contribution

The official definition of Classic McEliece, so designated by the project's own
Specification page (`spec.html` v2026.06.13: *"The official definition of Classic
McEliece is the cryptosystem specification"*). 16 pages. Defines the KEM over
binary Goppa codes in Niederreiter form: parameters, matrix reduction and
generation, encoding and decoding subroutines, key generation, fixed-weight
vector generation, encapsulation, decapsulation, byte-string representations,
and ten selected parameter sets.

## Key claims (as reported)

Provenance for every item below: `TASK-20260803-f3aece/parameter_sets.md`, a
committed transcription of this document at sha256 `dcc68788…`, independently
re-checked by validator `TASK-20260803-409c5e`. Values are cited with a `see:`
pointer rather than re-homed here, per the transcription convention
(`TASK-20260808-a9f648`, Rule 3.1.6).

- Parameters are (m, n, t) with q = 2^m, n <= q, t >= 2 and mt < n; the
  specification defines k = n − mt (Section 3). Definitional, not a claim.
- Ten selected parameter sets (Section 7): five (m, n, t) triples, each in a
  plain and an "f" (semi-systematic, (mu, nu) = (32, 64)) variant —
  (12, 3488, 64), (13, 4608, 96), (13, 6688, 128), (13, 6960, 119),
  (13, 8192, 128). `see:` `parameter_sets.md` §1.
- Symmetric parameters (Section 6.1): l = 256, H = the first 256 bits of
  SHAKE256, sigma_1 = 16, sigma_2 = 32.
- Size formulas (Section 6.2): public key is mt·ceil(k/8) bytes; ciphertext is
  ceil(mt/8) bytes.
- The document makes **no** security-category claim and states **no** numeric
  byte sizes. It delegates both, and the round-4 submission overview names the
  delegates explicitly: see [[KN-LIT-6da230]] (categories) and
  [[KN-LIT-7d2077]] (sizes).

### Code rates — DERIVED, NOT TRANSCRIBED

The rate k/n is **not printed in this document**; it follows from k = n − mt and
the Section 7 triples. `see:` `TASK-20260803-f3aece/parameter_sets.md` §2, which
is the locus-bearing home for these values and where the derivation is shown.
The exact rationals are authoritative over any decimal rendering of them
(convention Rule 2.1.7):

| Parameter set | k/n exact `[DERIVED]` |
|---|---|
| mceliece348864(f) | 85/109 |
| mceliece460896(f) | 35/48 |
| mceliece6688128(f) | 157/209 |
| mceliece6960119(f) | 5413/6960 |
| mceliece8192128(f) | 51/64 |

`formula:` k/n with k = n − mt · `formula_source:` this specification's Section 3
definition, as transcribed in `parameter_sets.md` §0 · `computation and gcd
reduction:` shown in `parameter_sets.md` §2 · **no rounding rule is declared in
this entry because this entry rounds nothing** — it carries exact rationals only,
and the decimal renderings and their range statement (`0.729167 … 0.796875`
`[DERIVED]`) stay at their home in `parameter_sets.md` §2, which the validator
recomputed 5/5.

## Relevance to this program

Primary source for `RQ-MCE-e65b3c` and `GOAL-MCE-001`. It supplies the rate k/n
that every rate-threshold claim in the alternant/Goppa distinguisher line
([[KN-LIT-4c8135]], [[KN-LIT-3c9f21]], [[KN-LIT-a4d70e]], [[KN-LIT-6b1fc8]])
must be compared against, and the exact (n, k, t) at which any memory-charged ISD
baseline for this goal must be computed.

**Stated flatly, because the comparison is the whole point of the goal and has
not been made:** none of those four distinguisher entries records a rate
threshold, so there is currently *nothing to compare these rates against*. This
entry supplies one side of a comparison and forecloses nothing on the attack
side, in either direction.

**Scoping trap, recorded by `TASK-20260803-f3aece` observation O3 and repeated
here because it is easy to walk into:** the ISO parameter-set list does not
include any mceliece348864 variant, while this document's Section 7 does. "The
standardized parameter sets" is therefore a strictly smaller set than "the
selected parameter sets", and 348864 is precisely the set [[KN-LIT-6da230]]
assigns the lowest category. Any deliverable using either phrase must say which
it means.

## Not verified here

- **This task read nothing.** `TASK-20260808-f9374d` is a coordinator task with
  no execute capability; it fetched no URL, ran no extractor, and computed no
  hash. Every value above is relayed from a committed BATCH-001 artifact, named
  at the point of use.
- Only Sections 3, 6 and 7 were read even by `TASK-20260803-f3aece`; the
  algorithm definitions in Sections 4 and 5 were not audited by anyone here.
- No implementation was run and no KAT was checked by this program.
- **Form caveat on the cited artifact, so it is not read as more than it is:**
  `parameter_sets.md` predates the settled transcription convention and
  `transcription_convention.md` §12 names five form non-conformances in it
  (V-1…V-5). Every one is a *form* non-conformance; the validator confirmed
  40/40 size cells exact and 5/5 rationals recomputed, and **no value error was
  found**. The values relayed above are the values that survived that check.

## Local copies

None. The PDF is third-party copyrighted material and is deliberately not
committed to this repository. The `sha256` in `identifiers` is the integrity
anchor: re-fetch the URL and compare.
