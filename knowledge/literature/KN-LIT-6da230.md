---
id: KN-LIT-6da230
type: literature
title: "Classic McEliece: conservative code-based cryptography: guide for security reviewers"
authors: []
authors_note: >-
  No author list on the title page; issued by the Classic McEliece team. The
  title page was read directly by TASK-20260808-1985f1 and its three printed
  lines are quoted verbatim in that task's `sec_table1.md` § Sources. Authors
  are NOT filled in from recall.
year: 2022
venue: "Classic McEliece round-4 NIST PQC submission, document dated 23 October 2022"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://classic.mceliece.org/mceliece-security-20221023.pdf"
  sha256: "db17ef0879cb8822120c312b7290f7db82fe9fc356bd16058ad334a512b523fa"
tags: [code-based, mceliece, isd, security-categories, memory-cost, structural-attacks, primary-source]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read`, and this is the ONE entry of this five-document family that earns it.
  TASK-20260808-1985f1 (GOAL-MCE-001, BATCH-a68f79 — the same batch as this
  entry) retrieved this document THREE times in this environment on
  2026-08-09Z — twice with curl and once with python urllib under TLS
  verification — each time HTTP 200, 332574 bytes, sha256 db17ef08…, 36 pages,
  and transcribed its Table 1 in full under the settled convention: 150/150
  cells agreeing across six extractor configurations across two independent
  retrievals, verified after writing against a third. SCOPE OF THE READ, stated
  because 36 pages were fetched and far fewer were read: Table 1 (printed page
  10), its caption, its column header row, the section 3.5 heading, the sentence
  introducing the table on page 9, and cost-model and scope sentences on pages
  10-11. THE REST OF THE DOCUMENT WAS NOT READ IN THIS ENVIRONMENT. Every claim
  below carries its own provenance marker so the boundary is visible per claim
  and not only here.
added: "2026-08-08"
superseded_by: null
---

## Contribution

36-page security discussion accompanying the round-4 submission. The round-4
submission overview delegates *"Expected strength (2.B.4) for each parameter
set"* and *"Analysis of known attacks (2.B.5)"* to this document, making it the
submission's designated source for security-category claims rather than a source
chosen by this program.

Its Table 1 reports the output of the Esser–Bellini security estimator for the
five selected Classic McEliece parameter sets under three memory-cost models.

## Provenance markers used below

| Marker | Means |
|---|---|
| **[SEC-READ]** | read first-hand in this environment by `TASK-20260808-1985f1` from the bytes at sha256 `db17ef08…`; quoted or pointed at in that task's `sec_table1.md` |
| **[B1-READ]** | read by `TASK-20260803-f3aece` on 2026-08-03 from a retrieval of the same URL whose recorded sha256 is byte-identical to the above; quoted in that task's `parameter_sets.md`. NOT re-read in this environment |
| **[B1-DRAFT]** | stated only in `TASK-20260803-f3aece`'s proposed-entry draft, with no supporting quotation in any transcription deliverable |

## Key claims (as reported)

These are the **submitters' assessments of their own scheme**. This entry relays
them and endorses none of them.

- **[SEC-READ]** Table 1 exists at printed page 10, is captioned *"Output of the
  Esser–Bellini estimator for the selected Classic McEliece parameter sets"*, and
  carries 15 rows × 10 columns: five parameter sets × three `mem` models, against
  the ten column headers `param mem Prange Stern Dumer BC BJMM pdw MO BM`. All
  150 values are transcribed; `see:` `TASK-20260808-1985f1/sec_table1.md`
  § TRANSCRIBED, which is their locus-bearing home. **No value is re-homed
  here.**
- **[SEC-READ]** The caption defines the `mem` column and nothing else: 0 for
  free memory access, 1/3 for a cube-root assumption, 1/2 for a square-root
  assumption. It adds *"Some cost components are ignored in all estimates."*
- **[SEC-READ]** **The table states no unit, at any of the five loci a unit could
  be stated**, and SEC states no definition anywhere for the column headers `BC`,
  `BJMM`, `pdw`, `MO`, `BM` — a full-text search of the 36-page extraction finds
  `BJMM` only in the header row and in bibliography entry [15], and the other
  four only in the header row. **What the numbers count is therefore not
  established by anything this program has read.**
- **[SEC-READ]** SEC's own prose names the smallest number in the table:
  *"the smallest number in the table, 140.8 for mceliece348864, is slightly below
  143"*, in the `mem` = 0 model.
- **[SEC-READ]** SEC then argues that number is an underestimate: *"the
  underlying estimator from [33] counts each vector operation as just 1
  operation: in particular, finding C collisions between two lists, each list
  containing L vectors, is assigned cost 2L + C, no matter what the vector length
  is"*, and *"The exact numbers in Table 1 should be expected to be superseded by
  larger numbers from future estimators that count bit operations."*
- **[SEC-READ]** SEC states that the 140.8 figure is *"for an attack using
  memory"* a printed power of two. **That exponent is NOT reproduced here.** The
  extraction flattens the superscript markup, `TASK-20260808-1985f1` recorded the
  raw bytes with a conjectured reading confined to a damage note, and convention
  Rule 5.2.4 forbids a conjectured reading from travelling into another document.
  A reader who needs the exponent must render the PDF at sha256 `db17ef08…`. The
  same applies to the two other powers of two in the quoted passages.
- **[B1-READ]** The submission *"continues to assign its selected parameter sets
  to 'categories' 1, 3, 5, 5, 5 respectively. As before, these assignments are
  based on counting realistic costs for memory."*
- **[B1-READ]** The same document states that if categories were assigned *"on
  the basis of bit operations with free memory access, then the correct
  assignments will instead be 1, 2, 4, 4, 5"*, and frames the two as **two cost
  models rather than a revision**: *"This does not reflect any instability in the
  Classic McEliece security estimates."*
- **[B1-READ]** / **[SEC-READ]** The "respectively" ordering is pinned by name at
  two of five positions, not guessed from word order: `parameter_sets.md` §3
  quotes SEC naming 6960119 as *"Category 5" (AES-256)* and 460896 as
  *"Category 3" (AES-192)*. The second of those sentences was independently
  re-read in this environment — `sec_table1.md` quotes it verbatim from printed
  page 11 — which corroborates the ordering at one position from a first-hand
  read.

## Relevance to this program

Directly bears on `GOAL-MCE-001`'s second completion criterion. It is a
primary-source statement of how the designers charge memory, and its Table 1 is a
published estimator output at exactly the parameters the goal must cost. Any
memory-charged ISD baseline this program builds should be compared against it
rather than derived in ignorance of it.

It does **not** settle the charging convention: `RQ-MCE-e65b3c` binds this goal
to the convention produced under `GOAL-HQC-001 TASK-20260802-0100a5` and forbids
deriving a competing one.

**What this entry does not license.** Nothing here is evidence that any Classic
McEliece parameter set is secure or insecure, or that it meets or misses any
category. `GOAL-MCE-001`'s claim-tier ceiling is **toy** and unchanged;
`active_hypothesis_ids` is empty and unchanged. Filing this entry establishes
that a published table says what it says, and no more. In particular the 140.8
figure is the source's report of a third-party estimator's output under an
accounting the source itself calls an underestimate — it is not this program's
estimate of anything.

## Not verified here

- **Table 1's numbers were transcribed, never reproduced.** No estimator was
  run, by this task or by `TASK-20260808-1985f1`. Nothing was recomputed,
  cross-checked arithmetically, or converted.
- **Reference [33], the Esser–Bellini estimator itself, was not obtained** by any
  task of this program. This is why the column headers and the unit of the
  numbers are unestablished, and it is the single highest-value cheap acquisition
  outstanding against this entry.
- **31 of the 36 pages were not read in this environment**, including SEC's
  arguments about memory-access cost beyond the sentences quoted above, and its
  treatment of structural attacks. The `structural-attacks` tag reflects the
  document's declared remit, not a read of that material.
- The category assignments are relayed as the submission's assertions. This
  program takes no position on whether any parameter set meets any category, and
  — reference [33] being unread — could not evaluate the question even if it were
  permitted to.
- `iacr:2026/1232`'s PDF was **not** attempted by this task or by
  `TASK-20260808-1985f1`, by any route. Its 403 is path-scoped and reproducible,
  circumvention is forbidden, and a blocked route is a recorded outcome
  (AGENTS.md rule 5).

## Local copies

None. The PDF is third-party copyrighted material and is deliberately not
committed to this repository. The `sha256` in `identifiers` is the integrity
anchor, and it has now been independently computed by two tasks on two different
hosts from three retrievals.
