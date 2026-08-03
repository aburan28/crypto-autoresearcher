---
id: KN-LIT-b7f8f8
type: literature
title: "Classic McEliece: conservative code-based cryptography: guide for implementors"
authors: []
authors_note: No author list on the title page; issued by the Classic McEliece team.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-impl-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-impl-20221023.pdf"
  sha256: "86225992a73a2dc986b2ef5edfcfa3e28d49684fffd8be281237e1e5af2757a3"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, key-sizes, implementation, constant-time, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml). Validator TASK-20260803-409c5e re-fetched it and
  independently verified ALL 40 cells of Table 1, because the private-key
  column has no arithmetic bridge to the specification. The agent that drafted
  this entry (TASK-20260803-a53f73) did NOT read the document. No local copy is
  committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
19-page implementors' guide; the submission overview delegates *"Detailed
performance analysis (2.B.2)"* to it. Its Table 1 is the primary source for the
numeric key, ciphertext and session-key sizes of all ten selected parameter sets.

## Key claims (as reported)
- **Table 1** (sizes in bytes; public key / private key / ciphertext / session
  key):
  - `mceliece348864` and `348864f`: 261120 / 6492 / 96 / 32
  - `460896` and `460896f`: 524160 / 13608 / 156 / 32
  - `6688128` and `6688128f`: 1044992 / 13932 / 208 / 32
  - `6960119` and `6960119f`: 1047319 / 13948 / 194 / 32
  - `8192128` and `8192128f`: 1357824 / 14120 / 208 / 32
- The private key *"can be compressed down to 40 bytes (or 32 bytes for non-f
  parameter sets) with uncompression less expensive than key generation"*, so the
  tabulated private-key column is the **uncompressed** form.
- The guide characterises the trade-off as large public keys with small
  ciphertexts, and notes use in PQ-WireGuard.

## Control run by this program
Every public-key and ciphertext figure in Table 1 was independently re-derived
from the specification's own size formulas and its `(m, n, t)` triples, matching
**10/10**, and that control was **independently re-run at 10/10** by
`TASK-20260803-409c5e` (`EV-MCE-332f99` O-1 `controls`). This cross-validates
this table and [[KN-LIT-48b4eb]] Section 7 simultaneously. **The private-key
column has no arithmetic bridge** and was verified by direct re-reading, not by
derivation.

## Relevance to this program
Supplies the concrete sizes for any cost or deployment statement about Classic
McEliece at the specification's parameter sets. Companion to [[KN-LIT-48b4eb]]
(parameters) and [[KN-LIT-7b78de]] (categories and memory-charged estimates).

## Not verified here
**No implementation was built, run, or benchmarked.** Timing and performance
claims in the guide were not examined. Table 1 covers only the ten non-pc sets;
**no numeric sizes for pc variants appear in any document read** — see
[[KN-LIT-209151]], where pc ciphertext sizes are computed from formulas rather
than transcribed. No local copy is committed.
