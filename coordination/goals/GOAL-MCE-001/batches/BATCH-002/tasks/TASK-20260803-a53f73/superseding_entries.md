# PROPOSED superseding knowledge entries — TASK-20260803-a53f73

**Task:** TASK-20260803-a53f73 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-002
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`
**Repo state at draft:** HEAD `2ea6216dda15f77044f5785144d8c0296dad9cc7`, branch
`claude/mceliece-bibliography-aggregate-7ogd0d`, working tree dirty only in this
task's own untracked artifact directory.

> **PROPOSED ONLY. NOTHING UNDER `knowledge/` WAS WRITTEN, EDITED, OR READ FOR
> MODIFICATION BY THIS TASK.** `knowledge/INDEX.md`, `knowledge/SOURCES.md` and
> `knowledge/sources.json` were not touched. Filing belongs to
> `TASK-20260803-3aa684` and only after both BATCH-002 reviews accept.

---

## 0. The form of a correction, and a divergence from BATCH-001 that must be settled

`knowledge/README.md` § Rules: *"Corrections supersede: write a new entry, set
`superseded_by` on the old one. Never silently rewrite substance (typo fixes
excepted)."*

**BATCH-001's producer proposed a different form and it is not the one the
corpus rules specify.** `TASK-20260803-292b99/corpus_provenance_upgrade.md` §0
proposed each correction as *"a **superseding addition to the entry body**, not
as a silent edit of an existing sentence"*, and §3.1 proposed `citation_verified`
and `tags` **diffs** applied to the existing files. Appending to an immutable
entry's body and rewriting its frontmatter is an **edit**, however it is
labelled: the file changes, the old text does not survive intact, and a reader
of the old ID gets the new claim. The red team endorsed that proposal in
substance (`red_team_report.md` §6a: *"correct in substance and correct in form
(superseding body addition, not a silent edit, per `knowledge/SEEDING.md`)"*),
but `knowledge/README.md`'s rule is the binding one and it says **new entry +
`superseded_by` on the old**.

**This package therefore uses the new-entry form throughout**, per named duty 1.
The divergence is recorded rather than quietly resolved, because a reviewer
comparing this package against BATCH-001's proposal will otherwise read the
change of form as an unexplained deviation. Nothing of substance from the
BATCH-001 proposals is dropped; it is carried into full replacement entries.

**Two writes per supersession, and both are mandatory.** Filing the new entry
without setting `superseded_by` on the old leaves two live contradictory entries
under two live IDs — strictly worse than the defect being repaired. The exact
`superseded_by` lines are given in §4 and repeated in `correction_log.yaml`.

---

## 1. SUPERSEDING ENTRY FOR `KN-LIT-4c8135` — new ID `KN-LIT-c4c2ac`

### 1.1 The defect, and the source sentences that establish it

**Defect D-4 as recorded** (`DEC-20260803-a5b9b1` D-4): *"UPHELD — KN-LIT-4c8135
states the boundary of arXiv:2304.14757 on the wrong axis. … The entry mentions
Goppa codes once, in the opposite direction, and frames the restriction as
rate-scoped while presenting that scoping as 'the whole content of its practical
reading'. The Goppa exclusion is absent."*

**The defective text, quoted from `knowledge/literature/KN-LIT-4c8135.md`
(lines 24–27 and line 31):**

> "Alternant codes are the family containing Goppa codes; the result is confined
> to the **high-rate** regime, and that scoping is the whole content of its
> practical reading."

> "- The attack is **rate-scoped** — it does not claim to break alternant or
> Goppa codes at arbitrary rate."

**The primary text that falsifies it**, from
`TASK-20260803-292b99/rate_regime_extraction.md` §3.3, transcribed from
`arXiv:2304.14757` full text at sha256
`ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`, re-acquired
byte-identically by validator `TASK-20260803-409c5e` (`EV-MCE-332f99` O-5):

> "Interestingly our attack does not work at all when the alternant code has the
> additional structure of being a Goppa code."

Table 1, same source, §3.1:

> "this paper    q “ 2 or q “ 3, m arbitrary + high rate condition (6)
>               (does not apply in the particular case of Goppa codes)"

§3.2 heading, same source: *"What is wrong with Goppa codes?"*, and
*"Goppa codes behave differently from random alternant codes and provide
counterexamples to Heuristic 18."*

### 1.2 INDEPENDENT MEASUREMENT — the count in the record is wrong, and the second occurrence is worse than the first

`DEC-20260803-a5b9b1` D-4 and `BATCH-002-OPENING` §2 both say the entry
*"mentions Goppa once"*. The red team's stated cheapest control was
`grep -c -i goppa knowledge/literature/KN-LIT-4c8135.md` → **1**
(`red_team_report.md` §6a).

**Re-measured by this task on HEAD `2ea6216d`:**

```
$ grep -c -i goppa knowledge/literature/KN-LIT-4c8135.md
2
$ grep -o -i goppa knowledge/literature/KN-LIT-4c8135.md | wc -l
2
```

Both the line count and the occurrence count are **2**, not 1. The control as
published in the red team report **does not reproduce**. The second occurrence
is at line 31 and it points the same wrong way as the first, more sharply:

> "The attack is **rate-scoped** — it does not claim to break alternant or Goppa
> codes at arbitrary rate."

Read against the paper, that sentence is a stronger error than the containment
sentence. Its natural contrapositive — the attack claims to break Goppa codes at
*high* rate — is precisely what the paper's own sentence denies. The correction
must therefore neutralise **both** occurrences, not one.

*This is a correction to the Coordinator's characterisation of the defect, not a
new defect in the entry.* It makes the defect larger, not smaller.

### 1.3 What the source actually says, and what the replacement must keep

The paper carries **three conjuncts**, not one, and dropping any of them
produces a new wrong entry:

1. **Code family** — generic alternant codes, and **explicitly not Goppa codes**.
2. **Field size** — `q ∈ {2, 3}`.
3. **Rate** — a high-rate condition, the paper's numbered condition (6).

Duty 2's warning applies here and is honoured: *a replacement that leads with the
exclusion while deleting the rate scoping has traded one wrong entry for
another.* The rate condition is real, is the paper's own, and is kept. What is
retracted is not the rate scoping but the claim that the rate scoping is *"the
whole content of its practical reading"*.

**Condition (6) itself remains NOT transcribed.** `rate_regime_extraction.md`
§3.4 reproduces the raw pdfminer output at that location and marks it
`[EXTRACTION-DAMAGED]`, stating: *"This inequality is NOT reconstructed and
carries no claim in any deliverable of this task."* The replacement entry
inherits that status verbatim. **The numeric rate threshold is still missing from
this program's records**, and the replacement says so as a recorded extraction
failure rather than an unattempted read.

### 1.4 Full replacement entry — file as `knowledge/literature/KN-LIT-c4c2ac.md`

```markdown
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
tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, polynomial-time, high-rate, small-field, not-goppa, goppa-excluded, groebner, algebraic-cryptanalysis]
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
```

---

## 2. SUPERSEDING ENTRY FOR `KN-LIT-71d1a0` — new ID `KN-LIT-819780`

### 2.1 A correction to the Coordinator's framing of this defect, stated first

`BATCH-002-OPENING` §2 says: *"The same framing is **wrong-typed** for
`KN-LIT-71d1a0`, which the correction must also fix: its Theorem 3 is stated in
the **dual** rate and says 'here we allow any R'; the 0.277 / 0.141 figures are
null-model conditions on a shortened code, not applicability bounds on the
distinguisher."* This task's handoff repeats it as *"Any entry stating otherwise
is wrong."*

**No entry states otherwise.** `knowledge/literature/KN-LIT-71d1a0.md` contains
no rate figure at all. Its "Not verified here" section says, verbatim:

> "The construction, its complexity, the code families and rates for which it
> succeeds, and whether it reaches Classic McEliece parameters are NOT recorded
> here."

The mis-typing lives in the **Coordinator's framing**, not in the entry:
`DEC-20260803-a5b9b1` D-2 `also_wrong_typed` records it as a property of *"the
same framing"* — `BATCH-001-OPENING` §4's *"the rate threshold is the whole
question"* — applied to `iacr:2024/1193`. The entry's defect is a **blank plus a
wrong tag**, and a blank is what let the framing be filled in wrongly.

That is the honest description and it changes what the correction must do. The
replacement entry does not retract a rate claim the old entry never made; it
**fills the blank from primary text** so it cannot be filled wrongly again, and
**removes the `key-recovery` tag**.

### 2.2 The tag defect and the source sentences that establish it

`DEC-20260803-a5b9b1` D-5: *"UPHELD — a tagging defect defeats RQ-MCE-e65b3c's
'distinguisher is not break' constraint at the grep level, at prevalence 4 of 4."*

The paper's own separation of the two notions, transcribed by
`TASK-20260803-292b99/corpus_provenance_upgrade.md` §2.2 from the full text at
sha256 `b69f8256133dcfd8c9d5dae196b8f653f5b956532a7ba949f400af3b902d68c0`,
VERBATIM:

> "Distinguishers address the decisional version of the problem […] Key recovery
> attacks address the computational version"

and its own statement of contribution, VERBATIM: *"We present a new distinguisher
for alternant and Goppa codes, whose complexity is subexponential in the
error-correcting capability, hence better than that of generic decoding
algorithms."*

`RQ-MCE-e65b3c.constraints`: *"Distinguisher is not break. … Any deliverable
naming a distinguisher states which it is."*

### 2.3 Full replacement entry — file as `knowledge/literature/KN-LIT-819780.md`

```markdown
---
id: KN-LIT-819780
type: literature
title: "The syzygy distinguisher"
authors:
  - "Hugues Randriambololona"
year: 2025
venue: "Eurocrypt"
identifiers:
  eprint: "iacr:2024/1193"
  doi: "10.1007/978-3-031-91095-1_12"
  arxiv: null
  url: "https://eprint.iacr.org/2024/1193"
source_artifact:            # NOT under `identifiers` -- see note in the task package
  url: "https://perso.telecom-paris.fr/randriam/maths/distingueur.pdf"
  sha256: "b69f8256133dcfd8c9d5dae196b8f653f5b956532a7ba949f400af3b902d68c0"
  bytes: 726538
  retrieved_at: "2026-08-03T03:14:08Z"
  retrieved_by: TASK-20260803-292b99
  committed_locally: false
  note: >-
    This is the AUTHOR'S COPY, not an ePrint or Springer file. See the version
    caveat in the body -- it is probably NOT the latest version.
tags: [code-based, mceliece, structural-attack, distinguisher, syzygy, commutative-algebra, alternant-codes, goppa, betti-numbers, subexponential, heuristic, dual-rate, algebraic-cryptanalysis]
confidence: reported
citation_verified: read
citation_verified_note: >-
  `read` is earned by TASK-20260803-292b99, which retrieved the full text from
  the sole author's institutional page (HTTP 200, 726,538 bytes,
  application/pdf, 2026-08-03T03:14:08Z, sha256 b69f8256...d68c0) and extracted
  it with pdfminer.six. Validator TASK-20260803-409c5e re-extracted the
  byte-identical file independently. No local copy is committed; the sha256 is
  the integrity anchor. The agent that drafted this entry
  (TASK-20260803-a53f73) worked from that task's committed transcription, not
  from a fresh extraction. SCOPED TO THE VERSION AT THAT HASH — see the version
  caveat below.
supersedes: KN-LIT-71d1a0
supersedes_reason: >-
  KN-LIT-71d1a0 carried the tag `key-recovery` on a distinguisher-only paper
  (DEC-20260803-a5b9b1 D-5), and left the paper's rate regime blank, which is
  the blank BATCH-001-OPENING section 4's framing filled in wrongly
  (DEC-20260803-a5b9b1 D-2 `also_wrong_typed`).
added: "2026-08-03"
superseded_by: null
---

## Contribution
**A distinguisher — not a key-recovery attack.** VERBATIM: *"We present a new
distinguisher for alternant and Goppa codes, whose complexity is subexponential
in the error-correcting capability, hence better than that of generic decoding
algorithms."* It uses syzygies — the relations among generators of a module, a
standard object of commutative algebra — to distinguish algebraic codes from
random ones. Eurocrypt 2025.

The paper separates the two notions itself, VERBATIM: *"Distinguishers address
the decisional version of the problem […] Key recovery attacks address the
computational version"*.

## THE RATE REGIME, STATED IN THE DUAL RATE — read this before comparing anything
This section exists because the superseded entry left the regime blank and the
blank was filled in wrongly downstream.

**Theorem 3 is stated in the DUAL rate**, VERBATIM: *"Asymptotically, q-ary
alternant (including Goppa) codes of **dual rate R** can be distinguished from
random codes […]"*. The complexity expression (formula 92) is
`[EXTRACTION-DAMAGED]` from the two-column PDF and is **NOT transcribed into this
corpus**.

**The paper explicitly declines a rate restriction on that theorem**, VERBATIM:

> "Fix a base field cardinality q, for instance q = 2, and a (dual) rate R. In
> [4] it is suggested to take a primal code of rate between 0.7 and 0.8, so
> passing to the dual gives 0.2 ≤ R ≤ 0.3. However here we allow any R."

**The numbers 0.277 and 0.141 are NOT applicability bounds on the
distinguisher.** They are conditions under which **Heuristic 1's prediction for
RANDOM codes** — the null model — is expected to hold. Remark 2, VERBATIM:

> "**Remark 2.** Consider this Heuristic in the asymptotic regime. Setting
> R = k/n, we can take d = dGV(q, n, k) ≈ H_q^{-1}(1 − R)n and
> d⊥ = dGV(q, n, n − k) ≈ H_q^{-1}(R)n the corresponding Gilbert-Varshamov
> distances, where H_q is the q-ary entropy function. Then the condition in 1.
> translates as H_q^{-1}(1 − R) > R(1 − R), and the condition in 2. translates
> as H_q^{-1}(R) > R², both of which are satisfied when R is small enough. In
> particular for q = 2, we find that 1. is satisfied for R < 0.277 and 2. is
> satisfied for R < 0.141."

The prose and the two numeric thresholds are **clean extraction**; the symbolic
conditions `H_q^{-1}(1 − R) > R(1 − R)` and `H_q^{-1}(R) > R²` are
`[EXTRACTION-DAMAGED — symbolic form only; the numeric thresholds are clean]`.

**And they are applied to a SHORTENED code, whose rate the proof argues is
o(1) by construction.** Proof of Theorem 3, VERBATIM: *"Moreover the shortened
code C_s has rate k_s/n_s = (k_{r*}+r)/(n−k+k_{r*}+r) = o(1), so by Remark 2
both conditions in Heuristic 1 are satisfied."* That is why the paper can also
write *"here we allow any R"*.

**Three traps, flagged and not resolved by this program:**
- `R` here is a **dual** rate. Comparing it against a primal `k/n` without
  converting is a category error.
- `0.277` and `0.141` are **null-model conditions**, not distinguisher
  applicability bounds.
- They are conditions on the **shortened** code, not on the McEliece code.

**This program does not adjudicate that chain of statements.** It is recorded as
the paper's own, quoted. No comparison against Classic McEliece's rates is
performed in this entry.

## Key claims (as reported)
- A distinguisher for alternant and Goppa codes built from syzygy computations,
  subexponential in the error-correcting capability.
- **Regime reach, the paper's own claim**, VERBATIM: *"Moreover it does not
  suffer from the strong regime limitations of the previous distinguishers or
  structure recovery algorithms: in particular, it applies to the codes used in
  the Classic McEliece candidate for postquantum cryptography standardization."*
  Quoted as the paper's claim; not verified, not adopted, not contradicted.
- VERBATIM: *"Since its introduction in 1978, this is the first time an analysis
  of the McEliece cryptosystem breaks the exponential barrier."* — carrying the
  paper's own footnote excluding attack-model results: *"we exclude results such
  as [28] that use an attack model for which direct countermeasures exist"*.
- **The complexity claim is CONDITIONAL and the paper says so in the sentence
  that introduces it**, VERBATIM: *"Now, under Heuristic 1, we have: Theorem 3.
  …"*. Qualitative consequence, in the paper's clean prose: *"the complexity of
  our distinguisher is subexponential in b (although, admittedly, only very
  slightly so)"*, with `ω ≈ 2.372` the exponent of linear algebra.
- **Unproven inputs, numbered by the paper:** Heuristic 1 (one statement, two
  parts) and Experimental facts 1–4. The paper flags all of them, states *"we
  will not be able to give proofs"*, gives partial theoretical arguments and
  sampling experiments, and records its own counterexamples (the Golay code for
  Experimental fact 2; *"one can find counterexamples"* for Experimental fact 3).
  Enumerated at
  `coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/heuristics_enumerated.md`
  §2.
- **The paper's own finite-parameter caveat, VERBATIM:** *"However this is only
  an asymptotic result: for concrete, finite parameters, such as those proposed
  in the Classic McEliece specification, a naive implementation of our
  distinguisher still falls beyond the best attacks by a non-negligible factor."*
  Its first open problem is *"Problem 1. Improve the implementation of this
  distinguisher."*
- On its Example 2 table, VERBATIM: *"These complexities improve those from [7],
  although they remain practically unreacheable and well beyond security
  levels."* (Source's spelling.)
- The paper reports that its Heuristic-1-based complexity estimate's precondition
  **fails for two of the five parameter triples it tabulates**, VERBATIM: *"We
  see this condition is satisfied for the parameter sets (3488, 12, 64),
  (6960, 13, 119), (8192, 13, 128), but for (4608, 13, 96) and (6688, 13, 128)
  it is not."* Lemma 5 is named as the fallback.

## VERSION CAVEAT — load-bearing
The retrieved file is the author's copy, self-described *"(Eurocrypt 2025
version, expanded, with supplementary material and errata)"*, dated 2025-05-02
in the site directory index. The ePrint record shows **"2025-10-16: last of 4
revisions"**. **This is therefore probably NOT the latest version, and every
claim recorded here is scoped to the sha256 in `identifiers`.** One difference
between the two retrieved versions is already visible: the ePrint abstract reads
*"an analysis (in the CPA model)"* where this PDF uses the footnote quoted above.

## Relevance to this program
Two distinct reasons, and they should not be collapsed.

**Methodological.** The strongest single example in this corpus of the move
`docs/inventor-protocol.md` is built around: **import a mature object from a
neighbouring area of mathematics and ask what it computes about the target.**
Syzygies come from commutative algebra and free-resolution theory, not from
coding theory, and the distinguisher exists because someone asked what they say
about a code. The corresponding ECDLP question — which established
algebraic-geometry or commutative-algebra invariants have not been computed
against curve-side objects — is exactly the kind this program is meant to
generate and then test cheaply before committing compute.

**Substantive, for RQ-MCE-e65b3c.** This is the paper `iacr:2026/1232` anchors
its subexponentiality claim to. Its regime is stated in the **dual** rate and its
asymptotic theorem explicitly declines a rate restriction; its finite-parameter
caveat is its own. Any deliverable of this program that compares a rate against
this paper must convert between primal and dual and must not read 0.277 / 0.141
as applicability bounds.

Held together with [[KN-LIT-7ee1a9]], [[KN-LIT-c4c2ac]] and [[KN-LIT-2127]] as
the modern distinguisher cluster.

**Does not bear on the ECDLP**, but is the corpus's best methodological exemplar
alongside [[KN-LIT-7965a1]].

## Why this entry supersedes KN-LIT-71d1a0
`KN-LIT-71d1a0` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-819780`.

Two defects, both recorded:

1. **The `key-recovery` tag** (`DEC-20260803-a5b9b1` D-5). This paper is a
   distinguisher and separates the two notions itself. `RQ-MCE-e65b3c` makes
   *"Distinguisher is not break"* a binding constraint and
   `docs/claims-and-verification.md` forbids promoting one to the other — a
   `key-recovery` tag is that promotion at the grep level. The tag is withdrawn
   here and appears nowhere in this entry's `tags`.
2. **The regime was blank.** The superseded entry recorded, verbatim, *"The
   construction, its complexity, the code families and rates for which it
   succeeds, and whether it reaches Classic McEliece parameters are NOT recorded
   here."* That was honest, but the blank is what `BATCH-001-OPENING` §4's *"the
   rate threshold is the whole question"* framing filled in wrongly
   (`DEC-20260803-a5b9b1` D-2 `also_wrong_typed`). **The superseded entry itself
   states no rate figure and asserts nothing wrong about the rate**; this entry
   fills the blank from primary text so it cannot be filled wrongly again.

`citation_verified` is upgraded `web → read` on the strength of the recorded
retrieval, scoped to the version caveat above.

## Not verified here
Citation verified against the IACR ePrint record for report 2024/1193 (title and
author list checked) on 2026-08-03; citation verified against the Crossref
record (DOI 10.1007/978-3-031-91095-1_12).

`confidence` stays `reported`: **nothing in this paper was re-derived or
reproduced by this program.** No complexity figure, benchmark, or security
estimate here has been reproduced.

**Not transcribed, deliberately:** formula (92); the κ complexity values in
Example 2 (`[EXTRACTION-DAMAGED]`, flattened superscripts); Heuristic 1's
symbolic conditions. The `(n, m, t)` triples in Example 2 are **this paper's
reproduction** of Classic McEliece parameters and are **not a substitute for the
Classic McEliece specification**.

**This entry asserts nothing about Classic McEliece's security in either
direction.** Sentences above that mention Classic McEliece are the paper's,
quoted.

Bibliographic line originally transcribed from the Classic McEliece project's
"Papers" page (https://classic.mceliece.org/papers.html, page version
2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md`.
Primary-text retrieval record:
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/source_access_log.yaml`.
```

---

## 3. What is deliberately NOT superseded here

- **`KN-LIT-7c4620` (`iacr:2026/1232`) stays `citation_verified: web` and is not
  superseded by this task.** Nobody in this program has read that paper. The
  provenance addition BATCH-001 proposed for it
  (`corpus_provenance_upgrade.md` §1) is a genuine improvement and is **not**
  folded into this package, because it is an abstract-level upgrade to an entry
  with no established defect, and this task's scope is the defects
  `DEC-20260803-a5b9b1` records. Flagged for the Coordinator as unfinished
  BATCH-001 business, not decided here.
- **No `confidence` upgrade anywhere.** Nothing was re-derived or reproduced;
  `reported` is the honest ceiling on every entry in this package.
- **No `KN-TECH` entry on ISD.** `DEC-20260803-a5b9b1`
  `knowledge_promotion.not_warranted` (3): a technique entry must state
  applicability conditions and known limits, and D-2 is a live demonstration
  that this program does not yet know them in this area. Unchanged by this task,
  which read no ISD paper.
- **No `KN-FIND`.** This program produced no internal result. Corrections to
  literature entries are not findings (`knowledge/SEEDING.md`: *"A literature
  entry never becomes a finding"*).

---

## 4. The `superseded_by` lines that must be set — EXACT

Each is a one-line frontmatter change on the **old** file, replacing
`superseded_by: null`. The old entries are otherwise **untouched**: same ID,
same body, same tags, same `added` date.

| Old file | Line to change | Replace with |
|---|---|---|
| `knowledge/literature/KN-LIT-4c8135.md` | line 20: `superseded_by: null` | `superseded_by: KN-LIT-c4c2ac` |
| `knowledge/literature/KN-LIT-71d1a0.md` | line 18: `superseded_by: null` | `superseded_by: KN-LIT-819780` |

Line numbers are as of HEAD `2ea6216d` and are given as an aid, not as a
guarantee; match on the literal string `superseded_by: null` in the frontmatter.

The tag-defect supersessions for `KN-LIT-13a01d`, `KN-LIT-7ee1a9` and
`KN-LIT-e37d4c` are in `tag_defect_corrections.md`, with their own
`superseded_by` table. `KN-LIT-71d1a0` is one of the four both-tagged entries and
is corrected **here** rather than there, because its defect is substantive as
well as tag-level and splitting it across two entries would create two
supersessions of one entry.

---

## 5. A schema point the filer must not get wrong: `sha256` does NOT belong under `identifiers`

Both replacement entries above carry their retrieval hash in a **top-level
`source_artifact:` block**, not inside `identifiers:`. This departs from the
BATCH-001 proposals, which put `sha256:` inside `identifiers:`
(`TASK-20260803-f3aece/proposed_kn_lit_entries.md`, all five proposed entries).

**Why, measured rather than asserted.** `tools/build_source_index.py`
`collect_literature()` walks `IDENTIFIER_ORDER = ("eprint","arxiv","doi","isbn","url")`
and then walks **every remaining key** of `identifiers` through
`canonical_identifier()`, whose fallback is `f"{kind}:{low}"`. A `sha256` key is
therefore emitted into `SOURCES.md` and `sources.json` as a bibliographic
identifier. Reproduced at HEAD `2ea6216d`:

```
$ python3 -c "... canonical_identifier over the proposed entry A identifiers ..."
identifiers -> ['url:classic.mceliece.org/mceliece-spec-20221023.pdf',
                'sha256:dcc6878852ef8a00a7bedd859da661770cf85d2c3d9239e06d25e4a0d365fd12']
```

A raw content hash presented as an identifier in the derived source index is
wrong output, and `SOURCES.md` is regenerated (`make sources`) rather than
hand-fixed, so it cannot be corrected downstream. A prose `sha256_note` key would
be worse — it would emit an entire sentence as an identifier.

`source_artifact:` is a **new frontmatter key** and appears nowhere else in
`knowledge/literature/` at HEAD `2ea6216d` (checked). `build_source_index.py`
ignores unknown top-level keys, so it is inert in the derived index; it is
carried purely so a reviewer can re-acquire and hash-compare. **If the
Coordinator prefers no schema extension, the hash belongs in the entry body
prose instead — but it must not go under `identifiers`.**

The same correction applies to the five specification entries; see
`specification_entries.md` §3.

---

## 6. Identifier allocation

| New ID | Allocated by | `--check` result on HEAD `2ea6216d` |
|---|---|---|
| `KN-LIT-c4c2ac` | `tools/allocate_id.py` `random_token()` (SystemRandom, 6-hex, no state scanned) | `OK: well-formed and free across the union` (9967 files scanned) |
| `KN-LIT-819780` | same | `OK: well-formed and free across the union` |

`tools/allocate_id.py --next` does not accept `KN-LIT` (its type list is
`batch, coordinator_decision, evidence, experiment, handoff, hypothesis, idea,
research_question`), so the tool's own `random_token()` allocator was invoked
directly and every candidate was rejected unless `occurrences()` returned empty.
**No `max+1` allocation was performed anywhere in this package** (CLAUDE.md /
AGENTS.md rule 14). The commands and outputs are reproduced in
`correction_log.yaml`.
