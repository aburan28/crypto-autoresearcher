---
id: KN-LIT-5ff88f
type: literature
title: "Polynomial time key-recovery attack on high rate random alternant codes (boundary completed: the Goppa exclusion is phase-scoped, present-tense, unproved, and conjectured by its authors to fall)"
authors:
  - "Magali Bardet"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2024
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/tit.2023.3334592"
  arxiv: "2304.14757v3"
  url: "https://arxiv.org/abs/2304.14757"
tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, generic-alternant, goppa-exclusion, polynomial-time, high-rate, small-field, algebraic-cryptanalysis, heuristic-conditional]
confidence: reported
citation_verified: transcription_of_full_text_at_recorded_sha256
citation_verified_note: >-
  NOT read in the session that wrote this entry. The four passages this entry
  adds were located and transcribed first-hand by validator session
  TASK-20260808-ea7bed (VAL-20260808-71bdb1, S-1), which re-fetched
  https://arxiv.org/pdf/2304.14757 BYTE-IDENTICAL to sha256
  ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8 and read it
  directly on 2026-08-08. One of the four is INDEPENDENTLY corroborated inside
  this program by BATCH-001's own committed transcription, checked directly by
  the writing session on 2026-08-09. The other three rest on that single
  validator session and have NOT been independently re-confirmed. The PDF is not
  stored in this repository; a reader who needs the primary object must
  re-acquire it at that sha256.
added: "2026-08-09"
supersedes: KN-LIT-c41d8b
superseded_by: null
---

## Why this entry exists

`DEC-20260808-a67816` D-5 found this program's correction of arXiv:2304.14757's
boundary **incomplete in one direction**, and bound the goal to completing it by
supersession. That completion landed on the **ledger** side as
`RQ-MCE-f8fca0` (`DEC-20260809-cb25a0`, BATCH-73a1b7), which is the binding
anchor and governs every deliverable of GOAL-MCE-001.

**This entry is the corpus half of the same completion, which BATCH-73a1b7 did
not write.** That batch added no `knowledge/` file, so the live corpus entry for
this paper — `KN-LIT-c41d8b` — still states the Goppa exclusion **unqualified**,
calling it "STRUCTURAL" and "the decisive conjunct". A reader reaching the paper
through the corpus rather than through `ledger/questions/` still gets the
incomplete reading. `VAL-20260808-71bdb1`'s own recommended remedy names both
halves: *"A superseding correction to KN-LIT-c41d8b and RQ-MCE-3f7c02 carrying
the four omitted passages, and closing the S-1a version gap (v3) and the S-1b
abstract-provenance seam. New records; do not edit."*

`KN-LIT-c41d8b` and `RQ-MCE-3f7c02` **stay in force and are not withdrawn** —
withdrawing them would restore a worse record (`DEC-20260808-a67816` D-4). Their
axis correction (code family, not rate) was right, and an independent validator
checked every quotation in them character for character and found them
**verbatim correct**. This entry adds the qualification they omitted, and closes
two provenance seams the same review opened.

## The four passages the superseded entry does not carry

Verbatim from arXiv:2304.14757**v3** at sha256
`ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`.

**Q-1 — page 7, the sentence immediately after the exclusion sentence.** The
paragraph's run-in heading is *"Opening the road for attacking the CFS scheme."*;
`KN-LIT-c41d8b` quotes the heading and the exclusion, and omits the sentence
that explains why the heading says *opening the road*:

> However this work could open the road for also attacking this subcase, in
> which case we could hope to break the CFS scheme [CFS01] which operates
> precisely in the high rate regime where the square of the dual of the Goppa
> code behaves abnormally.

**Q-2 — page 32, concluding remarks.** The authors conjecture their own
exclusion will fall:

> Therefore it is tempting to conjecture that Goppa codes, at least in the
> regime where they are distinguishable from random codes (which applies in
> particular to the CFS scheme [CFS01]) should eventually be attacked in
> polynomial by some variation the attack that has been given here.

(Transcribed **as printed**, including the source's own missing "of" after
"variation". Not silently repaired. The validator records this passage as
verified twice — poppler text extraction and a 150 dpi render of page 32 read
directly.)

**Q-3 — page 32, "Understanding the Gröbner basis approach".** This is the
passage that *scopes* the "does not work at all":

> However, unlike the case of the filtration where right now this part of the
> attack does not work at all, it seems that here even if the Gröbner basis
> computation consists of more steps, solving the whole system should still be
> polynomial.

It is the **filtration** phase that fails on Goppa codes, and it fails **"right
now"**. The authors expect the Gröbner phase to remain polynomial. The exclusion
is phase-scoped and present-tense, not a property of the result as a whole.

**Q-4 — page 15, section 3.2 opening ("What is wrong with Goppa codes?").** The
paper's own statement that its Goppa argument is not a proof:

> The discussion below does not represent a proof that computing a filtration
> is impossible for Goppa codes, but rather an intuition about what hampers it.

## What the boundary IS, completed

Unchanged from `KN-LIT-c41d8b`: a **conjunction of three conditions** — (1) code
family, generic/random alternant with Goppa codes excluded; (2) field size
`q ∈ {2,3}`, extension degree `m` arbitrary; (3) rate "sufficiently large (6)",
where condition (6) is **[EXTRACTION-DAMAGED]**, untranscribed by this program,
and may not be reconstructed. The three-conjunct decomposition was independently
checked and found **correct as far as it goes**.

What this entry adds is the qualification on conjunct 1. For binary Goppa codes,
conjunct 1 is where the paper's own applicability argument **terminates** — that
stands. What is withdrawn is the implication that this termination is
**permanent, proved, or whole-attack**:

| `KN-LIT-c41d8b` says | Completed reading |
|---|---|
| "Code family — **the decisive conjunct**" | Decisive *for where the paper's own argument stops*, and the paper says that stopping point is the **filtration phase only** (Q-3), holds **"right now"** (Q-3), is **not a proof** (Q-4), and is **conjectured to fall** (Q-2). |
| The exclusion is **STRUCTURAL** | The paper offers it as "an intuition about what hampers it" (Q-4), not as structure. Goppa codes are counterexamples to *its Heuristic 18* — an unvalidated heuristic of a third party's paper. |
| "the family conjunct settles applicability before any rate arithmetic is performed" | It settles what *this attack, as published, in its filtration phase* reaches. It settles nothing about a variation of it, which the authors expect to exist (Q-2). |

This is a **heuristic-conditional result** (Heuristics 18 and 23, and section
3.2's explicit "does not represent a proof"). This program has enumerated those
heuristics in BATCH-001's `heuristics_enumerated.md` and has **validated none of
them**. Any record leaning on the Goppa exclusion is leaning on an unvalidated
heuristic that the source itself flags as unproved.

## Two provenance seams, closed

**S-1a — the arXiv version, previously declared unrecoverable.**
`KN-LIT-c41d8b`'s "Not verified here" states the served version was not
recorded. It is recorded in the artifact itself: the PDF's left-margin stamp at
the bound sha256 reads **`arXiv:2304.14757v3 [cs.IT] 29 May 2023`**
(`VAL-20260808-71bdb1` S-1a, first-hand). All quotations here are from **v3**,
and this entry's frontmatter carries `arxiv: 2304.14757v3`.

**S-1b — a "verbatim" block that is not from the bound artifact. This one is a
correction, not an addition.** `KN-LIT-c41d8b` lines 80–83 quote the abstract as

```
when the code is {\em a generic alternant code} ... $q \in \{2,3\}$ and for {\em all} regime ...
```

inside a block labelled **verbatim** and attributed to the PDF at sha256
`ebbd94ac…`. The string `{\em` **does not occur anywhere in that PDF** (validator
grep count: 0). The PDF renders the same sentence without markup:

> when the code is a generic alternant code … q P t2, 3u and for all regime …

The **words are identical and no meaning is affected**; the LaTeX can only have
come from a different acquisition route (the arXiv abstract listing serves the
abstract's LaTeX source). But a block labelled verbatim and bound to a sha256
reproduced bytes that are not at that sha256 — in a line of work whose entire
method is hash-bound provenance. **The rendering above is what is at the bound
sha256; the LaTeX form is not, and is not attributed to it here.**

**Frontmatter/quotation mismatch, recorded not resolved.** This entry's
frontmatter describes the **IEEE journal version** (2024, IEEE Trans. IT, doi
`10.1109/tit.2023.3334592`) while every quotation is from **arXiv v3**. The two
may differ and **nobody in this program has read the journal version**. Carried
forward from `KN-LIT-c41d8b` as an open seam rather than silently reconciled.

## What this completion does NOT establish

- **Not a security statement about Classic McEliece, in either direction — and
  the change of direction does not become one.** Recording that the authors
  conjecture their exclusion will fall is a claim about *what the paper says*.
  Reading it as alarm is the mirror of the error being corrected.
- **Nothing about the 2026 line.** `KN-LIT-7c4620` (`iacr:2026/1232`) names
  binary Goppa codes in its abstract and its **body was not obtained** (403,
  path-scoped, reproducible; AGENTS.md rule 5 makes it a recorded outcome, never
  negative evidence). Neither the exclusion nor its qualification transfers.
- **No validation of Heuristics 18 or 23.** Q-2's conjecture is recorded at the
  *authors'* confidence, not this program's.
- **No claim tier above `toy`**, no hypothesis status change, no completion
  criterion of GOAL-MCE-001 met or approached.
- **No review of THIS entry.** It was written by a coordinator-only session on
  2026-08-09 and has **not** been independently reviewed.
- **It does not install a forward pointer at any superseded site**, and does not
  touch the corpus-wide `superseded_by` question. `DEC-20260809-cb25a0` D-3
  decided that question is **open**, assigned it to BATCH-73a1b7 scope item
  SUB-2, and declined both in-place annotation and sibling notice files. This
  entry respects that: `KN-LIT-4c8135` and `KN-LIT-c41d8b` both still carry
  `superseded_by: null`, so **a reader landing on either directly still sees no
  pointer**, and retrieval filtering on that field still surfaces them without
  marking them superseded. SUB-2 remains the fix.

## Provenance, and which half rests on what

The two halves have **different evidentiary bases** and are not interchangeable:

- **Q-1, Q-2, Q-3** rest on `VAL-20260808-71bdb1` alone — one independent
  session, first-hand at the bound sha256, recording its commands and outputs.
  **No second session has confirmed them.**
- **Q-4** has **two** independent bases: that report, and this program's own
  committed transcription at
  `coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/heuristics_enumerated.md`,
  section "A2 — Heuristic 23 … the Goppa carve-out", whose closing line reads
  *"Flagged unproven: yes; explicitly 'does not represent a proof'"*. The writing
  session **opened that file and confirmed both strings** on 2026-08-09 rather
  than accepting a prior report of the same check.
- **Page numbers** are the validator's, from its own first-hand read.
  `KN-LIT-c41d8b` correctly recorded that BATCH-001's transcription carried *no*
  page numbers and invented none; the basis changed, nothing was invented.

Everything inherited from `KN-LIT-c41d8b` — the exclusion sentence, Table 1's
restriction row, the section 3.2 heading, the body restatement — keeps that
entry's provenance chain and is not re-quoted here.

## Not verified here

- The full text was **not read in the session that wrote this entry**, and no
  fetch was performed by it.
- Condition (6) is **not** transcribed anywhere in this corpus, here included.
- The **IEEE journal version** is unread by anyone in this program.
- The paper's proof-of-concept implementation has not been fetched or run.
- No complexity figure, benchmark, or security estimate here has been reproduced
  by this program.

**Does not bear on the ECDLP.**

## Chain

Corpus: `KN-LIT-4c8135` (rate-scoped, defective) → `KN-LIT-c41d8b` (family axis
corrected, exclusion unqualified) → **`KN-LIT-5ff88f`** (exclusion qualified as
the source qualifies it; S-1a and S-1b closed).
Ledger anchor: `RQ-MCE-3f7c02` → `RQ-MCE-f8fca0` (`DEC-20260809-cb25a0`).
Authority: `DEC-20260808-a67816` D-5, on `EV-MCE-3d6e9a` O-4 and
`VAL-20260808-71bdb1` S-1, S-1a, S-1b.
Written 2026-08-09 by a coordinator-only harness session; **unreviewed**.
