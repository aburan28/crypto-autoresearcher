---
id: KN-LIT-c41d8b
type: literature
title: "Polynomial time key-recovery attack on high rate random alternant codes (boundary corrected: generic alternant only, Goppa codes explicitly excluded)"
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
tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, generic-alternant, goppa-exclusion, polynomial-time, high-rate, small-field, algebraic-cryptanalysis]
confidence: reported
citation_verified: transcription_of_full_text_at_recorded_sha256
citation_verified_note: >-
  NOT read in the session that wrote this entry. Every quotation below is
  re-quoted from this program's own committed verbatim transcription of the
  full text, made by TASK-20260803-292b99 on 2026-08-03 from
  https://arxiv.org/pdf/2304.14757 (HTTP 200, 526,690 bytes, 36 pages,
  sha256 ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8,
  pdfminer.six extraction), and independently re-acquired BYTE-IDENTICALLY at
  that sha256 by validator TASK-20260803-409c5e. The PDF itself is not stored
  in this repository (third-party PDFs are deliberately not committed), so the
  writing session could not re-read it and does not claim to have. A reader who
  needs the primary object must re-acquire it at that sha256.
added: "2026-08-08"
supersedes: KN-LIT-4c8135
superseded_by: null
---

## Why this entry exists

`KN-LIT-4c8135` states this paper's boundary **on the wrong axis**. It records
the restriction as a *rate* condition and calls that scoping "the whole content
of its practical reading", while the paper's own decisive restriction — for a
program studying Classic McEliece — is a **code-family exclusion**. The Goppa
exclusion is absent from that entry entirely; its one mention of Goppa codes
runs in the opposite direction.

That defect was upheld by `DEC-20260803-a5b9b1` D-4 (and its consequence
recorded as D-2), on evidence `EV-MCE-332f99` O-5. Knowledge entries are
immutable: `KN-LIT-4c8135` is **not edited**, and this entry supersedes it.
The same defect appears in two sibling sites, superseded in the same task
(`TASK-20260808-843c87`): `RQ-MCE-e65b3c.constraints` (superseded by
`RQ-MCE-3f7c02`) and `BATCH-001-OPENING.md` section 4 (superseded by the note
in that task's `correction_report.md`).

## The boundary the paper states, VERBATIM

The sentence that decides the code family. In the extracted text it stands
directly under the paragraph heading *"Opening the road for attacking the CFS
scheme."*:

> Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code.

The same restriction in the paper's **Table 1**, restriction column, row
*"this paper"*, verbatim as extracted:

```
this paper            q “ 2 or q “ 3, m arbitrary + high rate condition (6)
                      (does not apply in the particular case of Goppa codes)
```

(`“` is the pdfminer extraction's rendering of `=`; left as extracted and
annotated rather than silently normalised.)

The paper's **section 3.2** is headed *"What is wrong with Goppa codes?"* and
states, verbatim:

> Goppa codes behave differently from random alternant codes and provide
> counterexamples to Heuristic 18.

The **abstract** confines the positive answer the same way, verbatim:

> We give for the first time a positive answer for this problem when the code is
> {\em a generic alternant code} and when the code field size $q$ is small :
> $q \in \{2,3\}$ and for {\em all} regime of other parameters for which the
> aforementioned distinguisher works.

And the **body's own restatement of applicability**, verbatim:

> Here we break for the first time the m “ 2 barrier, which was even conjectured
> at some point to be the ultimate limit for such algebraic attacks to work in
> polynomial time and show that we can actually attack McEliece-alternant for any
> extension degree m provided that the rate of the alternant code is sufficiently
> large (6) and the field size sufficiently low q “ 2 or q “ 3.

**Location note, stated honestly:** the transcription records these locations —
the paragraph headed *"Opening the road for attacking the CFS scheme."*,
Table 1's restriction column, section 3.2, and the abstract — and records **no
page numbers**. None is invented here.

## What the boundary IS

A **conjunction of three conditions**, not a single rate threshold:

1. **Code family — the decisive conjunct.** Generic / random alternant codes.
   Goppa codes are **explicitly excluded**: the attack "does not work at all"
   on them, and the paper's stated reason is that Goppa codes are
   counterexamples to its Heuristic 18. The exclusion carves out exactly the
   subfamily Classic McEliece uses (binary Goppa codes).
2. **Field size.** `q ∈ {2,3}` ("the field size sufficiently low q = 2 or
   q = 3"), with the extension degree `m` **arbitrary** — breaking the earlier
   `m = 2` barrier is one of the paper's headline claims.
3. **Rate.** "the rate of the alternant code is sufficiently large (6)".
   Condition (6) is a lower bound on `n − 1`; **its formula is
   [EXTRACTION-DAMAGED] in the available extraction and is NOT transcribed by
   this program**. What is clean:
   `e := max{ i ∈ ℕ | r ≥ q^i + 1 } = ⌊log_q(r−1)⌋`.

The rate condition is **real and is not withdrawn** — the paper's own title
says *high rate*. What is withdrawn is the claim that the rate threshold is the
boundary, or the practically decisive one. For any question about **binary
Goppa** codes the family conjunct settles applicability before any rate
arithmetic is performed, and the distance in rate to Classic McEliece's
parameters is not the discriminator.

Read the title again with both halves live: *"high rate **random alternant**
codes"*. The family restriction was in the title all along;
`KN-LIT-4c8135` carried the title and read only the "high rate" half of it.

## What this correction does NOT establish

- **It is not a security statement about Classic McEliece, in either
  direction.** "Our attack does not work at all on Goppa codes" is these
  authors' statement about *their* attack. It is not a theorem that Goppa codes
  resist algebraic attacks, and this program asserts nothing about Classic
  McEliece's security here.
- **It says nothing about the 2026 line.** `KN-LIT-7c4620`
  (`iacr:2026/1232`) states *binary Goppa codes* explicitly in its abstract and
  its **body was not obtained** (Cloudflare challenge, path-scoped, recorded
  outcome under AGENTS.md rule 5). The exclusion in *this* paper does not
  transfer to that one.
- **It licenses no claim tier above `toy`** and moves no hypothesis status.

## Corrections to the superseded entry, itemised

The following statements in `KN-LIT-4c8135` are withdrawn by this entry. The
original text is preserved there and is not edited.

| Superseded text (verbatim from `KN-LIT-4c8135`) | Why |
|---|---|
| "the result is confined to the **high-rate** regime, and that scoping is the whole content of its practical reading" | The scoping is a three-conjunct conjunction; the family conjunct is the one that decides applicability to binary Goppa codes. |
| "The attack is **rate-scoped** — it does not claim to break alternant or Goppa codes at arbitrary rate." | Doubly wrong: it implies the attack *would* apply to Goppa codes at high rate. The paper says it "does not work at all" on Goppa codes, at any rate. |
| "The precise rate threshold … is the single most important number in the paper." | The single most important *statement* in this paper for this program is the Goppa exclusion. The rate threshold (condition (6)) remains untranscribed and extraction-damaged. |
| "Alternant codes are the family containing Goppa codes" (true, but used to bring the result *closer* to McEliece) | True as stated; the containment runs opposite to the paper's own restriction, which excludes the Goppa subfamily. |

`citation_verified` also moves: `KN-LIT-4c8135` carries `web` (bibliographic
line only, paper not read). This entry carries a transcription-based value with
the provenance chain spelled out in the frontmatter note, and deliberately
**not** `read` — nobody read the PDF in the session that wrote this entry.

## Relevance to this program

The corrected reading changes what this result is an exemplar *of*.
`KN-LIT-4c8135` taught it as the program's model of scope honesty while having
the scope wrong — which makes it, corrected, a sharper lesson: **a boundary
stated on a plausible axis is harder to catch than a boundary omitted.** The
rate axis was plausible (it is in the title), it was one of three real
conjuncts, and it was wrong as *the* boundary. The control that caught it was
one grep for "Goppa" over text the program had already retrieved.

**Does not bear on the ECDLP.**

## Not verified here

- The full text was **not read in the session that wrote this entry**. See the
  `citation_verified_note`.
- Condition (6) is **not** transcribed anywhere in this corpus, here included.
- The arXiv URL carried no version suffix when retrieved, so the served version
  number was not recorded; all quotations are scoped to sha256
  `ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`.
- The proof-of-concept implementation the paper names
  (`https://github.com/roccomora/HighRateAlternant`, recorded verbatim by
  `TASK-20260803-292b99`) has **not** been fetched or run by this program.
- No complexity figure, benchmark, or security estimate in this entry has been
  reproduced by this program.

## Provenance

- Transcription: `coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/attack_transcription.md` §3 and `rate_regime_extraction.md` §3.
- Retrieval log: same task's `source_access_log.yaml`, attempts C01, C02.
- Independent re-acquisition: `TASK-20260803-409c5e` validation report (C02 byte-identical).
- Authority for this correction: `DEC-20260803-a5b9b1` D-2, D-4; evidence `EV-MCE-332f99` O-5.
- Written by: `TASK-20260808-843c87` (GOAL-MCE-001, BATCH-a68f79).
