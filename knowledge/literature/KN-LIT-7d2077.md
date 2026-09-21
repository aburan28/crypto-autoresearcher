---
id: KN-LIT-7d2077
type: literature
title: "Classic McEliece: conservative code-based cryptography: guide for implementors"
authors: []
authors_note: >-
  No author list on the title page; issued by the Classic McEliece team. NOT
  filled in from recall.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-impl-20221023.pdf"
  sha256: "86225992a73a2dc986b2ef5edfcfa3e28d49684fffd8be281237e1e5af2757a3"
tags: [code-based, mceliece, key-sizes, implementation, constant-time, primary-source]
confidence: reported
citation_verified: web
citation_verified_note: >-
  NOT `read`. This document was retrieved and read by TASK-20260803-f3aece
  (BATCH-001) on 2026-08-03 — HTTP 200, 279687 bytes, sha256 86225992…, 19
  pages, `source_access_log.yaml` seq 9 — and its Table 1 was transcribed by two
  independent extractors that reconstruct to the same 10×4 array.
  TASK-20260808-f9374d, which files this entry, performed NO retrieval and read
  no PDF, and that read happened in a different session on a different host and
  branch. Per RQ-MCE-e65b3c's inherited caution from KN-OPEN-3f7a21, a `read`
  this task cannot attest is not claimed. UPGRADE PATH: re-fetch, compare
  against the sha256 above, transcribe under TASK-20260808-a9f648's convention.
added: "2026-08-08"
superseded_by: null
---

## Contribution

19-page implementors' guide. The round-4 submission overview delegates *"Detailed
performance analysis (2.B.2)"* to it. Its Table 1 (printed page 6) is the primary
source for the numeric key, ciphertext and session-key sizes of all ten selected
parameter sets — figures that appear nowhere in the cryptosystem specification
itself ([[KN-LIT-84b674]]).

## Key claims (as reported)

- **Table 1** gives public key / private key / ciphertext / session key sizes for
  the ten selected parameter sets. Its caption states the unit: *"Sizes of inputs
  and outputs to the complete cryptographic functions. All sizes are expressed in
  bytes."*

  **The values are not re-homed here.** `see:`
  `TASK-20260803-f3aece/parameter_sets.md` §4, which is their locus-bearing home
  (convention Rule 3.1.6), where all 40 cells sit with their provenance and were
  independently verified **40/40 exact** by validator `TASK-20260803-409c5e`.
  A summary that repeats forty numbers without their locus is exactly how a value
  drifts loose from its source, and this entry declines to be that summary.
- **[B1-DRAFT — stated only in `TASK-20260803-f3aece`'s proposed-entry draft,
  with no supporting quotation in any transcription deliverable, and not
  re-verified here]** The private key *"can be compressed down to 40 bytes (or 32
  bytes for non-f parameter sets) with uncompression less expensive than key
  generation"*, so the tabulated private-key column is the uncompressed form.
- **[B1-DRAFT — same caveat]** The guide characterises the trade-off as large
  public keys with small ciphertexts, and notes use in PQ-WireGuard.

## Relevance to this program

Supplies the concrete sizes for any cost or deployment statement about Classic
McEliece at standardized parameters.

Its main value to this program is as an **independent arithmetic control rather
than as a fact sheet.** Every public-key and ciphertext figure in its Table 1 was
re-derived in `TASK-20260803-f3aece` from the specification's own formulas
(public key mt·ceil(k/8) bytes, ciphertext ceil(mt/8) bytes) and the (m, n, t)
triples, matching **10/10**. Two documents transcribed separately, one arithmetic
relation between them, and the relation held — which cross-validates this table
and the specification's Section 7 simultaneously. That control is worth more than
either transcription alone, and it is the reason this entry can be filed at
`citation_verified: web` without the numbers being in doubt.

## Not verified here

- **This task read nothing** and computed nothing. `TASK-20260808-f9374d` has no
  execute capability.
- No implementation was built, run, or benchmarked by this program. Timing and
  performance claims in the guide were not examined by anyone here; the
  `constant-time` tag reflects the document's declared subject matter, not a read
  of that material.
- Table 1 covers only the ten non-`pc` sets. **No numeric size table for the `pc`
  variants appears in any document this program has read.** The `pc` ciphertext
  sizes that appear in this program's task artifacts are computed from formulas
  and are marked as computed; see [[KN-LIT-4fa25d]].
- **Form caveat on the cited artifact:** `parameter_sets.md` predates the settled
  transcription convention, and `transcription_convention.md` §12 names its §4
  as V-5 (unit stated in prose after the table rather than on it). That is a form
  non-conformance; the unit is sourced from the caption and all 40 cells verified
  exact.

## Local copies

None. Third-party copyrighted material, deliberately not committed. The `sha256`
in `identifiers` is the integrity anchor.
