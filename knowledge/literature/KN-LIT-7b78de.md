---
id: KN-LIT-7b78de
type: literature
title: "Classic McEliece: conservative code-based cryptography: guide for security reviewers"
authors: []
authors_note: No author list on the title page; issued by the Classic McEliece team.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-security-20221023.pdf"
source_artifact:
  url: "https://classic.mceliece.org/mceliece-security-20221023.pdf"
  sha256: "db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa"
  retrieved_by: TASK-20260803-f3aece
  committed_locally: false
tags: [code-based, mceliece, isd, security-categories, memory-cost, structural-attacks, esser-bellini, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-f3aece, which fetched this PDF on
  2026-08-03 (HTTP 200; URL, byte count and sha256 in that task's
  source_access_log.yaml) and extracted it with two independent extractors.
  Validator TASK-20260803-409c5e re-fetched it and read the re-fetched Table 1
  directly. The agent that drafted this entry (TASK-20260803-a53f73) did NOT
  read the document. No local copy is committed.
added: "2026-08-03"
superseded_by: null
---

## Contribution
36-page security discussion accompanying the round-4 submission. The round-4
submission overview delegates *"Expected strength (2.B.4) for each parameter
set"* and *"Analysis of known attacks (2.B.5)"* to this document — the delegating
sentence *"See the separate "guide for security reviewers" document"* was
confirmed in the overview by the validator — making it the submission's own
designated source for security-category claims.

## Key claims (as reported — THE SUBMITTERS' ASSESSMENTS OF THEIR OWN SCHEME)
Every bullet here is the submitters' assertion. This entry relays them and
**endorses none of them.**

- The submission assigns its selected parameter sets to categories
  *"1, 3, 5, 5, 5 respectively"* — i.e. 348864 → 1, 460896 → 3, 6688128 → 5,
  6960119 → 5, 8192128 → 5 — stating these are *"based on counting realistic
  costs for memory"*. (The `respectively` mapping is an inference, not a
  transcription; it was independently traced and confirmed by
  `TASK-20260803-409c5e` from the document's own row order and two explicit
  antecedents.)
- The same document states that under free-memory bit-operation accounting
  *"the correct assignments will instead be 1, 2, 4, 4, 5"*, and frames the two
  as **two cost models rather than a revision**.
- **Table 1 (p. 10) reports Esser–Bellini estimator output for all five sets
  under three memory models (`mem = 0, 1/3, 1/2`).** The lowest tabulated entry
  read by `TASK-20260803-f3aece` is **140.8** for `mceliece348864` at `mem = 0`.
- The document argues the estimator's numbers **underestimate** bit operations
  because it *"counts each vector operation as just 1 operation"*, and that the
  140.8 figure corresponds to an attack using memory `2^86.6`.

**The full cell-by-cell transcription of Table 1 is NOT in this entry.** It is
dispatched as `TASK-20260803-cb44ab` (GOAL-MCE-001 BATCH-002). This entry states
only what `TASK-20260803-f3aece` read; a reader needing the table must go to that
task's deliverable or to the PDF at the sha256 above.

## Relevance to this program
Directly bears on `GOAL-MCE-001`'s second completion criterion: a primary-source
statement of **how the designers charge memory**, with a published estimator
output at exactly the parameters this goal must cost. Any memory-charged ISD
baseline this program builds should be compared against it rather than derived in
ignorance of it.

**This document does NOT settle a costing convention for this program, and this
program is bound to none.** `DEC-20260802-344883` D-6 records
*"ISD-FC-2026 IS NOT ADOPTED … a usable draft, not a binding convention"*, and
`GOAL-HQC-001.next_action` says *"DO NOT bind GOAL-SDITH-001 to ISD-FC-2026."*
`DEC-20260803-a5b9b1` D-3 retracts the contrary claim that any binding existed.
**Reading this document is not adopting its convention, and citing its numbers
requires citing its model alongside them** — a cost figure without its memory
model is not a baseline.

## Not verified here
**Table 1's numbers were read but NOT reproduced, and no estimator was run by
this program.** The document's arguments about memory-access cost were not
evaluated. The security categories are relayed as the submission's assertions;
**this program takes no position on whether any parameter set meets any
category**, and no statement here bears on Classic McEliece's security in either
direction. Only the passages named above were read closely. No local copy is
committed.
