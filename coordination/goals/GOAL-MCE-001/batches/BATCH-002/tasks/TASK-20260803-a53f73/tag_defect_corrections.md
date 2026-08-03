# PROPOSED tag-defect corrections — TASK-20260803-a53f73

**Task:** TASK-20260803-a53f73 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-002
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`
**Measured on:** HEAD `2ea6216dda15f77044f5785144d8c0296dad9cc7`

> **PROPOSED ONLY. NOTHING UNDER `knowledge/` WAS WRITTEN OR MODIFIED.**

---

## 1. The defect, and the source sentences that establish it

`DEC-20260803-a5b9b1` D-5, UPHELD:

> "a tagging defect defeats RQ-MCE-e65b3c's 'distinguisher is not break'
> constraint at the grep level, at prevalence 4 of 4. … The four are
> KN-LIT-13a01d, 71d1a0, 7ee1a9, e37d4c. KN-LIT-13a01d carries key-recovery
> while its own body reads 'It does not recover keys; it distinguishes' — and it
> is the entry RQ-MCE-e65b3c names as the anchor of that very constraint."

The constraint it defeats, from `ledger/questions/RQ-MCE-e65b3c.yaml`
`constraints`, VERBATIM:

> "Distinguisher is not break. KN-LIT-13a01d distinguishes and does not recover
> keys; docs/claims-and-verification.md forbids promoting one to the other. Any
> deliverable naming a distinguisher states which it is."

The self-contradiction inside the anchor entry, from
`knowledge/literature/KN-LIT-13a01d.md` lines 26–29, VERBATIM:

> "It does not recover keys; it distinguishes, in the high-rate regime, and that
> was enough to unsettle a foundational assumption."

and lines 43–45:

> "Report a distinguisher as a distinguisher — this program's claim tiers
> (`docs/claims-and-verification.md`) forbid promoting it to a break."

while its frontmatter (line 18) reads:

```
tags: [code-based, mceliece, structural-attack, key-recovery, distinguisher, high-rate, goppa, algebraic-cryptanalysis, foundational]
```

---

## 2. INDEPENDENT RE-MEASUREMENT — not copied from the red team

Named duty 4: *"Verify the prevalence yourself before proposing — do not take
this number on trust."* Measured by this task with its own parser, not by
reusing the red team's script or its numbers.

**Method.** Parse the YAML frontmatter of every `knowledge/**/*.md`, extract the
`tags:` list with a regex anchored to the frontmatter block, and count set
membership. Whole corpus, all four provenance classes, not only the 137 entries
filed 2026-08-03. Zero files failed to parse (7807/7807 literature entries
yielded a `tags` list). The script is reproduced in §6.

### 2.1 The 137 entries filed 2026-08-03 — the red team's stated population

| Quantity | Red team (`red_team_report.md` §6b) | This task | Agree? |
|---|---:|---:|---|
| entries filed 2026-08-03 | 137 | **137** | yes |
| tagged `key-recovery` | 36 | **36** | yes |
| tagged `distinguisher` | 4 | **4** | yes |
| tagged **both** | 4 | **4** | yes |
| tagged `distinguisher` **without** `key-recovery` | 0 | **0** | yes |

The four are the same four: `KN-LIT-13a01d`, `KN-LIT-71d1a0`, `KN-LIT-7ee1a9`,
`KN-LIT-e37d4c`. **Prevalence within that population: 4 of 4.** The red team's
measurement reproduces exactly.

### 2.2 CORPUS-WIDE — the measurement the red team explicitly did not run

The red team bounded its own claim (`red_team_report.md` §6b): *"This is a
tag-versus-title-and-body check over the 137 entries filed 2026-08-03. It does
**not** cover the 32 pre-existing McEliece entries, does not cover the ~7,670
non-McEliece entries."* That check is run here.

| Population | files | `key-recovery` | `distinguisher` | **both** | `distinguisher` only |
|---|---:|---:|---:|---:|---:|
| `knowledge/literature/` (whole corpus) | 7807 | **50** | **7** | **4** | **3** |
| `knowledge/techniques/` | 83 | 2 | 2 | **0** | 2 |
| `knowledge/findings/` | 31 | 0 | 0 | 0 | 0 |
| `knowledge/open-problems/` | 26 | 0 | 0 | 0 | 0 |
| **corpus total** | **7947** | **52** | **9** | **4** | **5** |

**The defect does NOT extend beyond the four.** Corpus-wide there are exactly
four both-tagged entries and they are the same four `DEC-20260803-a5b9b1` D-5
names. No pre-existing entry and no non-McEliece entry carries the pair.

**The corpus-wide prevalence is 4 of 7, not 4 of 4.** Three literature entries
carry `distinguisher` without `key-recovery` — `KN-LIT-109`, `KN-LIT-110`,
`KN-LIT-7587`, all lattice/LWE dual-attack entries added 2026-07-24, none in the
McEliece line. The techniques corpus adds two more correctly single-tagged
entries (`KN-TECH-039`, `KN-TECH-077`).

**What that changes, stated carefully.** It does *not* soften the defect: within
the McEliece structural line every distinguisher-tagged entry is mis-tagged, and
that line is exactly the one `RQ-MCE-e65b3c` queries. It *does* narrow the
diagnosis. "The sweep produced zero correctly-tagged distinguisher-only entries"
is confirmed for the 2026-08-03 sweep; "the corpus has no correctly-tagged
distinguisher-only entry" would be false, and the corpus's own prior practice
(`KN-LIT-109/110/7587`, `KN-TECH-039/077`) is the counterexample that shows the
correct tagging was already available. The defect is local to the 2026-08-03
McEliece sweep.

### 2.3 Boundaries on this measurement, stated so it is not over-read

- It is a **tag-set membership** measurement. It cannot find a distinguisher
  paper that carries neither tag, and it makes no judgement about whether any
  paper's `key-recovery` tag is *substantively* right beyond the four examined
  below.
- It is measured at HEAD `2ea6216d` on branch
  `claude/mceliece-bibliography-aggregate-7ogd0d`. Another worktree may hold
  entries this tree does not.
- It does **not** establish that anything consumes these tags. No consumer was
  looked for by this task; `BATCH-002-OPENING` §3's claim that *"a future agent
  grepping `key-recovery` to find breaks gets four distinguishers back"* is a
  claim about a query nobody has been shown to run, and challenging it is
  assigned to the red team (`TASK-20260803-9ab856` named duty 3). **This task
  does not assert that harm and does not rest any correction on it.** The
  correction rests on the narrower and checkable ground that `KN-LIT-13a01d`'s
  tags contradict its own body and the RQ constraint it anchors.

---

## 3. Per-entry justification — what the source actually says

A tag is a claim, so removing one needs the same discipline as removing a
sentence. Each of the three below is assessed on what this program has actually
read.

| Entry | Paper | Was the paper read? | Basis for removing `key-recovery` |
|---|---|---|---|
| `KN-LIT-13a01d` | Faugère–Gauthier–Otmani–Perret–Tillich, `iacr:2010/331` | **No** | The entry's **own body** states *"It does not recover keys; it distinguishes"* and *"A **distinguisher**, not a key-recovery attack — the separation is explicit."* The tag contradicts the entry, and the entry is `RQ-MCE-e65b3c`'s named anchor. |
| `KN-LIT-7ee1a9` | Lemoine–Mora–Tillich, `iacr:2025/531` | **Abstract only** | The abstract, read by TASK-20260803-292b99 at sha256 `88035f1a…bfb299`, states *"Computing HF(2) still gives a polynomial time **distinguisher** for alternant or Goppa codes"* and frames distinguishing as *"a first step before being able to attack McEliece"* — the paper places the key recovery elsewhere ([BMT24]). |
| `KN-LIT-e37d4c` | Wiemers, `iacr:2025/1661` | **No** | Weakest case; see §3.1. |

### 3.1 `KN-LIT-e37d4c` — the case that must not be overstated

**Nobody in this program has read `iacr:2025/1661`.** Its entry says so:
*"The note's actual observation is NOT recorded here"* and *"The full text was
**not read** for this entry."*

So the removal cannot be justified as *"the paper is a distinguisher and not a
key recovery"* — that would be a claim about an unread paper, which is exactly
the failure `KN-OPEN-3f7a21` and `DEC-20260803-a5b9b1` D-2 record. The
defensible justification is narrower and is the one used:

**Nothing this program holds supports the `key-recovery` tag on this entry.**
The entry's own body describes *"a contribution to understanding when Goppa
codes can be distinguished from random"* and *"Note-length: a focused
observation rather than a full attack"*; the ePrint title recorded in the same
entry is *"Distinguishing Goppa codes using higher-order vanishing"*. A tag
asserting key recovery with no read source behind it is an unsupported claim,
and the correction removes an unsupported claim rather than asserting its
negation.

The replacement entry says this explicitly and adds `unread` to its own "Not
verified here" section, so a later reader who *does* read the paper can restore
a `key-recovery` tag by supersession if the paper turns out to claim one. **The
correction is not a finding about the paper.**

### 3.2 `KN-LIT-71d1a0` is corrected elsewhere

`KN-LIT-71d1a0` is the fourth both-tagged entry. It is superseded in
`superseding_entries.md` §2 (new ID `KN-LIT-819780`) rather than here, because
its defect is substantive as well as tag-level and one entry may not be
superseded twice in one batch. Its `key-recovery` tag is removed there.

---

## 4. Full replacement entries

### 4.1 `KN-LIT-13a01d` → new ID `KN-LIT-6b5b72`

```markdown
---
id: KN-LIT-6b5b72
type: literature
title: "A distinguisher for high rate McEliece cryptosystems"
authors:
  - "Jean-Charles Faugère"
  - "Valérie Gauthier"
  - "Ayoub Otmani"
  - "Ludovic Perret"
  - "Jean-Pierre Tillich"
year: 2010
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: "iacr:2010/331"
  doi: "10.1109/itw.2011.6089437"
  arxiv: null
  url: "https://eprint.iacr.org/2010/331"
tags: [code-based, mceliece, structural-attack, distinguisher, high-rate, goppa, algebraic-cryptanalysis, foundational]
confidence: reported
citation_verified: web
supersedes: KN-LIT-13a01d
supersedes_reason: >-
  KN-LIT-13a01d carried the tag `key-recovery` while its own body read "It does
  not recover keys; it distinguishes", and it is the entry RQ-MCE-e65b3c names
  as the anchor of its "distinguisher is not break" constraint.
  DEC-20260803-a5b9b1 D-5.
added: "2026-08-03"
superseded_by: null
---

## Contribution
**A distinguisher for high-rate McEliece cryptosystems** — the paper that broke
the long-standing belief that Goppa codes were indistinguishable from random
codes. It does not recover keys; it distinguishes, in the high-rate regime, and
that was enough to unsettle a foundational assumption.

## Key claims (as reported)
- High-rate Goppa/alternant public keys are distinguishable from random.
- A **distinguisher**, not a key-recovery attack — the separation is explicit.
- Confined to high rate.

## Relevance to this program
The origin of the modern structural line and, for this program, an important
case study in **what a distinguisher is worth.** It did not break McEliece. It
did invalidate a security-reduction step that had been treated as safe, and it
opened the research direction that produced [[KN-LIT-819780]],
[[KN-LIT-c4c2ac]] and [[KN-LIT-2127]] fifteen years later.

Two disciplines follow. Report a distinguisher as a distinguisher — this
program's claim tiers (`docs/claims-and-verification.md`) forbid promoting it to
a break, **and that prohibition binds the tag line as well as the prose**. And
take a distinguisher seriously anyway, because the assumption it refutes may be
load-bearing elsewhere.

This entry is `RQ-MCE-e65b3c`'s named anchor for its constraint *"Distinguisher
is not break."*

## A scoping note carried over and corrected
The superseded entry read: *"The high-rate scoping repeats the pattern of
[[KN-LIT-4c8135]]: real result, bounded regime, and the bound is the practically
decisive part."* The comparison to `KN-LIT-4c8135` is **withdrawn as stated**:
`arXiv:2304.14757` is bounded on three axes at once — code family (explicitly
**not** Goppa), field size `q ∈ {2,3}`, and a high-rate condition — and calling
its rate bound "the practically decisive part" is the single-axis reading
`DEC-20260803-a5b9b1` D-4 upheld as a defect. See [[KN-LIT-c4c2ac]].

**This paper's own high-rate scoping is unaffected by that withdrawal**, and is
restated unchanged above. Nothing here says the rate bound of this 2010 paper is
not load-bearing; what is withdrawn is the claim that the *other* paper's rate
bound is its whole boundary.

## Why this entry supersedes KN-LIT-13a01d
`KN-LIT-13a01d` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-6b5b72`.

The defect (`DEC-20260803-a5b9b1` D-5): the superseded entry carried
`key-recovery` in its `tags` while its Contribution section read *"It does not
recover keys; it distinguishes"* and its Relevance section instructed *"Report a
distinguisher as a distinguisher."* The research question's canonical example of
the rule was a grep-level violation of the rule. The tag is withdrawn; the body
text, which was already correct, is carried over.

**No content claim about the paper changed.** This is a tag correction and a
withdrawn cross-reference, executed as a supersession because
`knowledge/README.md` admits no other form.

## Not verified here
Citation verified against the IACR ePrint record for report 2010/331 (title and
author list checked) on 2026-08-03; citation verified against the Crossref
record (DOI 10.1109/itw.2011.6089437).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page
(https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved
2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The rate threshold and the distinguisher's mechanism are NOT recorded here.

The full text was **not read** for this entry, and was not read for the
supersession either. Everything under "Key claims" is relayed, not re-derived,
and no complexity figure, benchmark, or security estimate in this entry has been
reproduced by this program.
```

### 4.2 `KN-LIT-7ee1a9` → new ID `KN-LIT-45b1b2`

```markdown
---
id: KN-LIT-45b1b2
type: literature
title: "Understanding the new distinguisher of alternant codes at degree 2"
authors:
  - "Axel Lemoine"
  - "Rocco Mora"
  - "Jean-Pierre Tillich"
year: 2025
venue: "Designs, Codes and Cryptography"
identifiers:
  eprint: "iacr:2025/531"
  doi: "10.1007/s10623-025-01626-8"
  arxiv: null
  url: "https://eprint.iacr.org/2025/531"
source_artifact:            # NOT under `identifiers`; see superseding_entries.md section 5
  kind: abstract_page_only
  url: "https://eprint.iacr.org/2025/531"
  sha256: "88035f1a7a0f59750cbaf89a770295643f0e9a111d72b43bbb6d9ad497bfb299"
  retrieved_by: TASK-20260803-292b99
  committed_locally: false
  note: >-
    ABSTRACT PAGE ONLY. The full text was not obtained; see
    citation_verified_note.
tags: [code-based, mceliece, structural-attack, distinguisher, alternant-codes, goppa, algebraic-cryptanalysis]
confidence: reported
citation_verified: web
citation_verified_note: >-
  Stays `web`, deliberately. The FULL TEXT WAS NOT OBTAINED:
  inria.hal.science/hal-05461754/document and .../hal-04953992/document both
  returned HTTP 200 whose body is a proof-of-work bot interstitial rather than
  a PDF (not circumvented), and the ePrint PDF endpoint is
  Cloudflare-challenged. Only the ePrint ABSTRACT was read
  (TASK-20260803-292b99, HTTP 200, sha256 88035f1a...bfb299). Under
  knowledge/SEEDING.md a `read` flag would assert that this entry's claims
  reflect the paper's real content; they reflect its abstract.
supersedes: KN-LIT-7ee1a9
supersedes_reason: >-
  KN-LIT-7ee1a9 carried the tag `key-recovery` on a paper its own abstract
  describes as a distinguisher. DEC-20260803-a5b9b1 D-5.
added: "2026-08-03"
superseded_by: null
---

## Contribution
Explains the **new distinguisher of alternant codes at degree 2** — an analysis
paper clarifying why a recently discovered distinguisher works, rather than
introducing a new one. **This is a distinguisher result, not a key recovery**;
its abstract frames distinguishing as *"a first step before being able to attack
McEliece"* and places the key recovery elsewhere ([BMT24]). Alternant codes are
the family containing Goppa codes, so a distinguisher there bears on McEliece's
structural assumption; what it bears is not established by this program.

## Key claims (as reported, from the ABSTRACT only)
- An explanation of the mechanism behind the degree-2 alternant distinguisher.
- Understanding-oriented: the contribution is the reason, not the attack.
- VERBATIM: *"Computing $\mathrm{HF}(2)$ still gives a polynomial time
  distinguisher for alternant or Goppa codes and is apparently able to
  distinguish Goppa or alternant codes in a **much broader regime of rates** as
  the one of [FGO+11]."* **The abstract's own hedge — "apparently" — is
  preserved and must not be dropped.**
- On the reach of the earlier distinguisher, VERBATIM: *"Whereas the
  distinguisher of [FGO+11] is only able to distinguish Goppa codes or alternant
  codes of **rate very close to 1**, in [CMT23a] a much more powerful (and more
  general) distinguisher was proposed."*
- VERBATIM: *"The value of $\mathrm{HF}(2)$ corresponding to random linear codes
  is known and this yields **a precise description of the new regime of rates**
  that can be distinguished by this new method."*

## THE RATE REGIME IS ANNOUNCED IN THE ABSTRACT AND LIVES IN THE BODY, WHICH WAS NOT OBTAINED
The abstract says a precise description of the new rate regime exists. **This
program does not hold it.** The regime for this paper is **NOT TRANSCRIBED**, and
the fact that it exists is not a substitute for having it. Any deliverable of
this program that needs this paper's rate regime must obtain the body first.

## Relevance to this program
Held for the genre as much as the content. Papers whose contribution is
**understanding why an existing attack works** are how a field converts a
surprising result into a predictive theory — and predictive theory is what tells
you which *other* parameters are affected.

This program has the same obligation in its own lifecycle: `/review-evidence`
requires the mechanism to be stated, not only the outcome, because an
unexplained empirical win cannot be scoped and therefore cannot be safely
generalised.

Held together with [[KN-LIT-6b5b72]], [[KN-LIT-819780]] and [[KN-LIT-c4c2ac]] as
the modern distinguisher cluster.

**Does not bear on the ECDLP.**

## Why this entry supersedes KN-LIT-7ee1a9
`KN-LIT-7ee1a9` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-45b1b2`.

The defect (`DEC-20260803-a5b9b1` D-5): the superseded entry carried
`key-recovery` in its `tags`. The paper's own abstract calls the object a
distinguisher and places the key recovery in another work. `RQ-MCE-e65b3c`
constrains *"Distinguisher is not break … Any deliverable naming a distinguisher
states which it is"*, and `docs/claims-and-verification.md` forbids promoting one
to the other — a `key-recovery` tag is that promotion at the grep level. The tag
is withdrawn.

Two additions carry over from `TASK-20260803-292b99`, which read the abstract:
the paper's own rate-regime sentences (quoted above, with the "apparently"
hedge), and the explicit statement that the precise regime was **not obtained**.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/531 (title and
author list checked) on 2026-08-03; citation verified against the Crossref
record (DOI 10.1007/s10623-025-01626-8).

**The full text was NOT read.** Only the ePrint abstract was obtained, at the
sha256 in `identifiers`. Everything under "Key claims" is relayed from that
abstract, not re-derived, and no complexity figure, benchmark, or security
estimate in this entry has been reproduced by this program. The mechanism
explained, and its consequences for Goppa codes at Classic McEliece parameters,
are NOT recorded here.

**This entry asserts nothing about Classic McEliece's security in either
direction.**

Bibliographic line transcribed from the Classic McEliece project's "Papers" page
(https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved
2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.
Retrieval record:
`coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/source_access_log.yaml`.
```

### 4.3 `KN-LIT-e37d4c` → new ID `KN-LIT-15c85b`

```markdown
---
id: KN-LIT-15c85b
type: literature
title: "A note on the Goppa code distinguishing problem"
authors:
  - "Andreas Wiemers"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/1661"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1661"
tags: [code-based, mceliece, structural-attack, goppa, distinguisher, indistinguishability, unread]
confidence: reported
citation_verified: web
supersedes: KN-LIT-e37d4c
supersedes_reason: >-
  KN-LIT-e37d4c carried the tag `key-recovery`, which nothing this program has
  read supports. DEC-20260803-a5b9b1 D-5. The removal asserts nothing about the
  paper's content, which remains unread.
added: "2026-08-03"
superseded_by: null
---

## Contribution
A note on the **Goppa code distinguishing problem** — the assumption, separate
from syndrome decoding, that a Goppa code's public generator matrix cannot be
told apart from a random one. McEliece's security needs both, and the
distinguishing assumption is the weaker-understood of the two.

## Key claims (as reported)
- A contribution to understanding when Goppa codes can be distinguished from
  random.
- Note-length: a focused observation rather than a full attack.

**Both bullets are relayed from a bibliography line and an ePrint title. The
paper has not been read by anyone in this program.**

## Relevance to this program
The distinguishing problem is where **all the structural attacks in this section
live**, and it is the part of McEliece's security that rests on the least
theory. Held as part of that thread ([[KN-LIT-6b5b72]], [[KN-LIT-819780]],
[[KN-LIT-45b1b2]]).

The transferable observation for this program is architectural: a cryptosystem
built on a hidden-structure trapdoor has **two** assumptions, and the one about
the structure being hidden is usually the softer one. Any ECDLP-side proposal
introducing a structured object should expect its structural assumption, not its
hardness assumption, to be the first thing attacked.

## Why this entry supersedes KN-LIT-e37d4c
`KN-LIT-e37d4c` is retained unchanged under its own ID and marked
`superseded_by: KN-LIT-15c85b`.

The defect (`DEC-20260803-a5b9b1` D-5): the superseded entry carried
`key-recovery` in its `tags`.

**The justification for removal is narrow and is stated narrowly, because the
paper is unread.** This entry does NOT claim the paper is a distinguisher result
and not a key recovery — that would be a claim about a document nobody here has
opened, which is the failure mode `KN-OPEN-3f7a21` and `DEC-20260803-a5b9b1` D-2
record. The claim made is only this: **nothing this program holds supports a
`key-recovery` tag on this entry.** The entry's own body describes a contribution
to the *distinguishing* problem and a note-length observation; the ePrint title
recorded below is *"Distinguishing Goppa codes using higher-order vanishing"*.
An unsupported tag is removed; its negation is not asserted.

If a later task reads `iacr:2025/1661` and finds a key-recovery claim in it, the
correct response is a new superseding entry restoring the tag with the source
sentence attached — not a repair of this one.

## Not verified here
Citation verified against the IACR ePrint record for report 2025/1661 (title and
author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page
(https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved
2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The note's actual observation is NOT recorded here. **Title drift:** the
bibliography lists this as "A note on the Goppa code distinguishing problem",
but the current IACR ePrint record for report 2025/1661 is titled
*"Distinguishing Goppa codes using higher-order vanishing"*. This entry keeps the
bibliography's title as listed and records the ePrint title here; the two were
reconciled during verification, not assumed equal.

**The full text was NOT read**, for the original entry or for this supersession.
Everything under "Key claims" is relayed, not re-derived, and no complexity
figure, benchmark, or security estimate in this entry has been reproduced by this
program. The `unread` tag is carried in `tags` so this state is greppable.
```

---

## 5. The `superseded_by` lines that must be set — EXACT

Two writes per supersession. Filing a new entry without marking the old one
leaves two live contradictory entries under two live IDs and is the worst
outcome available here.

| Old file | Frontmatter line | Replace with |
|---|---|---|
| `knowledge/literature/KN-LIT-13a01d.md` | `superseded_by: null` | `superseded_by: KN-LIT-6b5b72` |
| `knowledge/literature/KN-LIT-7ee1a9.md` | `superseded_by: null` | `superseded_by: KN-LIT-45b1b2` |
| `knowledge/literature/KN-LIT-e37d4c.md` | `superseded_by: null` | `superseded_by: KN-LIT-15c85b` |
| `knowledge/literature/KN-LIT-71d1a0.md` | `superseded_by: null` | `superseded_by: KN-LIT-819780` (set in `superseding_entries.md` §4, listed here only for completeness of the four) |

**Cross-reference hazard for the filer.** Nine existing entries link to the
superseded IDs by `[[KN-LIT-...]]` wikilink. Those links are in **immutable
entries** and must **not** be rewritten; the supersession chain is what a reader
follows. The new entries above link to each other's new IDs, so the corrected
cluster is internally consistent from the new side. This is recorded as a known,
accepted consequence of the supersede-don't-edit rule, not as an oversight.

---

## 6. Reproduction — the measurement script

Run from the repository root. Output is the table in §2.2.

```python
import glob, re, os

def tags_of(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    m = re.search(r'^tags:\s*\[(.*?)\]\s*$', t.split('---', 2)[1], re.M | re.S)
    return [x.strip().strip('"\'') for x in m.group(1).split(',') if x.strip()] if m else None

def added_of(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    a = re.search(r'^added:\s*"?([0-9-]+)"?', t.split('---', 2)[1], re.M)
    return a.group(1) if a else None

for d in ['knowledge/literature', 'knowledge/techniques',
          'knowledge/findings', 'knowledge/open-problems']:
    fs = sorted(glob.glob(d + '/*.md'))
    rs = [(p, tags_of(p)) for p in fs]
    assert all(t is not None for _, t in rs), 'unparsed frontmatter'
    kr    = [p for p, t in rs if 'key-recovery' in t]
    di    = [p for p, t in rs if 'distinguisher' in t]
    both  = [p for p, t in rs if 'key-recovery' in t and 'distinguisher' in t]
    donly = [p for p, t in rs if 'distinguisher' in t and 'key-recovery' not in t]
    print(d, len(fs), len(kr), len(di), len(both), len(donly),
          [os.path.basename(p) for p in both])
```

Restricting to `added_of(p) == '2026-08-03'` inside `knowledge/literature`
reproduces §2.1.

**Recorded environment:** Python 3.11.15; repository at HEAD `2ea6216d`, branch
`claude/mceliece-bibliography-aggregate-7ogd0d`; no network access used by this
measurement.

---

## 7. Identifier allocation

| New ID | Supersedes | `--check` on HEAD `2ea6216d` |
|---|---|---|
| `KN-LIT-6b5b72` | `KN-LIT-13a01d` | `OK: well-formed and free across the union` |
| `KN-LIT-45b1b2` | `KN-LIT-7ee1a9` | `OK: well-formed and free across the union` |
| `KN-LIT-15c85b` | `KN-LIT-e37d4c` | `OK: well-formed and free across the union` |

All minted with `tools/allocate_id.py`'s own `random_token()` allocator
(`random.SystemRandom`, 6-hex, no state scanned) and confirmed with
`python3 tools/allocate_id.py --check <ID>`. **No `max+1` allocation was
performed.** Full commands and outputs in `correction_log.yaml`.
