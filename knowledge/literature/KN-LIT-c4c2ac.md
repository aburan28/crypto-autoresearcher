---
id: KN-LIT-c4c2ac
type: literature
title: "Polynomial time key-recovery attack on high rate random alternant codes"
authors:
  - "Magali Bardet"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2024
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: null
  doi: "10.1109/tit.2023.3334592"
  arxiv: "2304.14757"
  url: "https://arxiv.org/abs/2304.14757"
source_artifact:            # NOT under `identifiers` -- see note in the task package
  url: "https://arxiv.org/pdf/2304.14757"
  sha256: "ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8"
  bytes: 526690
  retrieved_at: "2026-08-03T03:16:58Z"
  retrieved_by: TASK-20260803-292b99
  committed_locally: false
tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, polynomial-time, high-rate, small-field, goppa-excluded, groebner, algebraic-cryptanalysis]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-292b99, which retrieved the full text
  (https://arxiv.org/pdf/2304.14757, HTTP 200, 526,690 bytes, PDF v1.4, 36
  pages, 2026-08-03T03:16:58Z, sha256 ebbd94ac...c564b8) and read it
  SELECTIVELY BY TARGETED SEARCH, not cover to cover. Validator
  TASK-20260803-409c5e re-acquired the same bytes and confirmed the hash.
  No local copy is committed; the sha256 above is the integrity anchor. The
  agent that drafted this entry (TASK-20260803-a53f73) worked from that task's
  committed transcription, not from a fresh extraction of the PDF.
supersedes: KN-LIT-4c8135
supersedes_reason: >-
  KN-LIT-4c8135 stated this paper's boundary on the wrong axis. See
  "Why this entry supersedes KN-LIT-4c8135" below. DEC-20260803-a5b9b1 D-4.
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **polynomial-time key-recovery attack on high-rate random alternant codes**,
which **does not apply to Goppa codes**. The paper states the exclusion itself,
VERBATIM:

> "Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code."

Its Table 1 records the restriction for this paper as *"q “ 2 or q “ 3, m
arbitrary + high rate condition (6) (does not apply in the particular case of
Goppa codes)"* (`“` is the extraction's rendering of `=`), and §3.2 is titled
*"What is wrong with Goppa codes?"*, stating *"Goppa codes behave differently
from random alternant codes and provide counterexamples to Heuristic 18."*

Classic McEliece uses binary Goppa codes. **This entry states that adjacency and
draws no consequence from it in either direction**; what the exclusion means for
any scheme is not established by this program.

## The stated restriction is THREE conjuncts, not one
All three are the paper's own, and none may be quoted without the others.

1. **Code family** — *generic alternant* codes, **explicitly NOT Goppa codes**.
   The abstract confines the positive answer, VERBATIM: *"We give for the first
   time a positive answer for this problem **when the code is a generic
   alternant code** and when the code field size $q$ is small : $q \in \{2,3\}$"*.
2. **Field size** — VERBATIM: *"the field size sufficiently low q “ 2 or q “ 3"*.
3. **Rate** — VERBATIM: *"show that we can actually attack McEliece-alternant for
   any extension degree m provided that the rate of the alternant code is
   sufficiently large (6)"*. The rate condition is real and is retained here;
   what is retracted from the superseded entry is the claim that the rate
   scoping is the whole of the paper's practical reading.

**Condition (6) is NOT transcribed and carries no claim in this corpus.** The
two-column ligature-heavy typesetting interleaves its terms beyond reliable
reordering; the raw extraction is preserved and marked `[EXTRACTION-DAMAGED]` at
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/rate_regime_extraction.md`
§3.4. A reviewer wanting condition (6) must read the rendered PDF at the sha256
in `identifiers`. What IS clean: (6) is a **lower bound on `n − 1`**, i.e. a
large-`n`-relative-to-`rm` condition — which is what "high rate" means here —
and `e := max{ i ∈ ℕ | r ≥ q^i + 1 } = ⌊log_q(r−1)⌋`. **The qualitative reading is
labelled as such and is not a substitute for the formula. The numeric rate
threshold remains UNRECORDED by this program.**

## Key claims (as reported)
- Polynomial-time key recovery for random alternant codes of high rate, for
  `q ∈ {2,3}` and arbitrary extension degree `m`.
- **The attack does not work at all on Goppa codes** (the paper's own sentence,
  quoted above).
- The polynomial-time claim is **conditional on heuristics and the paper says so
  in the same sentence**, VERBATIM: *"By using certain heuristics that we
  confirmed experimentally we are able to prove that the Gröbner basis
  computation takes polynomial time and give a complete algebraic explanation of
  each step of the computation."*
- Numbered unproven inputs found by TASK-20260803-292b99: **Conjecture 18,
  Heuristic 23, Assumption 28, Assumption 29 (High rate regime, q ≥ 3),
  Assumption 30 (High rate regime, q = 2)**, plus at least one unnumbered
  heuristic step. **Enumeration NOT certified complete**
  (`TASK-20260803-292b99/heuristics_enumerated.md` §3).
- A discrepancy is recorded and not repaired: the prose refers to *"Heuristic
  18"* while the numbered statement at 18 is labelled *"Conjecture 18"*.
- The paper's own restatement of reach, VERBATIM: *"we have at the end a way to
  break a McEliece scheme based on binary or ternary alternant codes as soon as
  (A_r(x,y)^⊥)^{*2} is not the full code F_q^{n−1}"* (star-product markup
  `[EXTRACTION-DAMAGED]`), and *"This would allow to break the McEliece scheme
  **as soon as the code rate is large enough** and would break all instances of
  the CFS signature scheme."*
- CFS context, VERBATIM: *"we could hope to break the CFS scheme [CFS01] which
  operates precisely in the high rate regime"*.
- Published in IEEE Transactions on Information Theory, i.e. it has been through
  journal review.

## Relevance to this program
This entry is held for the **scope discipline** it demonstrates and for the
correction it now carries. A result may be bounded on more than one axis at once,
and the axis a reader notices first is not necessarily the decisive one. Here the
paper carries a family exclusion, a field-size condition and a rate condition
simultaneously; quoting the rate condition alone produced a corpus entry
(`KN-LIT-4c8135`) that read as closer to Classic McEliece than the paper claims.

The operational lesson, stated as a procedure rather than a moral: **when
recording a restricted result, enumerate every conjunct of the restriction and
say which are unrecorded.** A single-axis summary of a multi-axis restriction is
the failure this entry exists to prevent, and it is the failure this entry's
predecessor committed.

**Does not bear on the ECDLP.**

## Why this entry supersedes KN-LIT-4c8135
`KN-LIT-4c8135` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-c4c2ac`. It is superseded, not deleted, and its text is
part of this program's honesty record.

The defect (`DEC-20260803-a5b9b1` D-4, upheld from
`TASK-20260803-08e883/red_team_report.md` §6a): the superseded entry mentions
Goppa codes **twice**, both times pointing away from the paper's actual boundary,
and recorded the rate scoping as *"the whole content of its practical reading"*.
Its two Goppa sentences were:

> "Alternant codes are the family containing Goppa codes; the result is confined
> to the **high-rate** regime, and that scoping is the whole content of its
> practical reading."

> "The attack is **rate-scoped** — it does not claim to break alternant or Goppa
> codes at arbitrary rate."

The second is the more damaging: its natural contrapositive is that the attack
*does* claim to break Goppa codes at high rate, which the paper's own sentence
denies. (`DEC-20260803-a5b9b1` D-4 and `BATCH-002-OPENING` §2 both say "once";
`TASK-20260803-a53f73` re-measured the corpus file and found **two** occurrences,
so the published cheapest control `grep -c -i goppa` → 1 does not reproduce. The
correction is larger than the record states, not smaller.)

Nothing in the superseded entry's rate scoping is discarded here. The rate
condition is the paper's and is restated above; only the claim that it is the
*whole* reading is retracted.

## Not verified here
Citation verified against the arXiv record for 2304.14757 and against the
Crossref record (DOI 10.1109/tit.2023.3334592), 2026-08-03.

Full text obtained and read **selectively by targeted search, not cover to
cover** (TASK-20260803-292b99). Heuristic enumeration is **not certified
complete**. **Condition (6) is not transcribed**, so the numeric rate threshold —
the single number the superseded entry correctly flagged as most important — is
still not held by this program, now as a recorded extraction failure.

No complexity figure, benchmark, or security estimate in this entry has been
reproduced by this program. The MAGMA proof-of-concept the paper points to
(*"A proof-of-concept implementation in MAGMA of the whole attack can be found at
https://github.com/roccomora/HighRateAlternant"*) was **not fetched**.

**This entry asserts nothing about Classic McEliece's security in either
direction.** Sentences above that mention Goppa codes or McEliece are the
paper's, quoted at its own hedging level.

Bibliographic line originally transcribed from the Classic McEliece project's
"Papers" page (https://classic.mceliece.org/papers.html, page version
2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md`.
Primary-text retrieval record:
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/source_access_log.yaml`.
