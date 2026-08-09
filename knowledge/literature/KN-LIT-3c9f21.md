---
id: KN-LIT-3c9f21
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
tags: [code-based, mceliece, structural-attack, distinguisher, high-rate, goppa, algebraic-cryptanalysis, foundational, claim-class-corrected]
supersedes: [KN-LIT-13a01d]
confidence: reported
citation_verified: web
citation_verified_note: >-
  Inherited, not re-earned. KN-LIT-13a01d records a 2026-08-03 verification of
  this bibliographic line against the IACR ePrint record for report 2010/331 and
  against the Crossref record for the DOI. TASK-20260808-f9374d performed NO
  retrieval of any kind and read no full text; it re-tagged. The value is `web`
  because that is what the recorded verification supports, and it is not raised
  to `read` because nobody in this program has read this paper.
added: "2026-08-08"
superseded_by: null
---

## Why this entry exists

**It supersedes `KN-LIT-13a01d` on one point only: the claim-class tags.**

`KN-LIT-13a01d` carries both `distinguisher` and `key-recovery`. That pair is
incoherent for this paper by the superseded entry's own text — *"It does not
recover keys; it distinguishes"* — and it makes `RQ-MCE-e65b3c`'s standing
constraint *"Distinguisher is not break"* unauditable by anything except human
reading. This entry drops `key-recovery` and keeps `distinguisher`, per
`knowledge/TAG-CLAIM-CLASS.md` rule R-CC-1.

`KN-LIT-13a01d` is **not edited**. It stands as written, immutable, and is
retired by being named in this entry's `supersedes:` field (rule R-CC-6).

**Nothing else changed.** Not the citation, not the claims, not the confidence,
not the relevance assessment, and not the verification status. A reader looking
for a substantive correction will not find one here.

**Where the mis-tagging came from, as far as it can be traced.** All four
entries corrected in this batch were filed on 2026-08-03 by the GATHER-20260803
sweep, and all four carry the same `structural-attack, key-recovery,
distinguisher` prefix. It has the shape of a tag block applied to a cluster
rather than a judgement made per paper. That is an inference from the pattern,
not an established fact about how the sweep ran, and it is recorded as the
former.

## Claim class

`distinguisher`. The subject distinguishes high-rate Goppa/alternant public keys
from random; it claims no key recovery and no message recovery.

**On what basis, and how far that basis reaches.** On the title and on
`KN-LIT-13a01d`'s own recorded description, which states the separation
explicitly. **This program has not read the paper.** The classification is
therefore as strong as a relayed abstract and no stronger.

**Falsification condition, stated so it can be checked rather than assumed:** if
a read of the full text shows the paper claims key recovery in any regime, this
classification is wrong and this entry must itself be superseded under a new id.
Re-tagging it in place would be the same error this entry corrects.

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
opened the research direction that produced [[KN-LIT-a4d70e]] (superseding
[[KN-LIT-71d1a0]]), [[KN-LIT-4c8135]] and [[KN-LIT-2127]] fifteen years later.

Two disciplines follow. Report a distinguisher as a distinguisher — this
program's claim tiers (`docs/claims-and-verification.md`) forbid promoting it to
a break. And take a distinguisher seriously anyway, because the assumption it
refutes may be load-bearing elsewhere.

The high-rate scoping repeats the pattern of [[KN-LIT-4c8135]]: real result,
bounded regime, and the bound is the practically decisive part.

`RQ-MCE-e65b3c` names this paper as one of four whose rate threshold must be
stated as a quantitative distance from Classic McEliece's actual rates. Those
rates are now transcribed: see [[KN-LIT-84b674]]. **The threshold in this paper
is not, and this entry supplies no number to compare against them.**

## Not verified here

The full text was **not read** for this entry, and was not read for
`KN-LIT-13a01d` either. Everything under "Key claims" is relayed at one further
remove — it is copied from the superseded entry, which copied it from a
bibliography line. No complexity figure, benchmark, rate threshold or security
estimate has been reproduced by this program.

The rate threshold and the distinguisher's mechanism are NOT recorded here.

Bibliographic line originally transcribed from the Classic McEliece project's
"Papers" page (https://classic.mceliece.org/papers.html, page version
2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md`.

**Inherited inconsistency, recorded rather than resolved (AGENTS.md rule 8).**
The `venue` field names a journal, *IEEE Transactions on Information Theory*,
while the `doi` field's string is `10.1109/itw.2011.6089437`, whose `itw.2011`
component is the shape of an IEEE Information Theory *Workshop* proceedings
identifier. Both strings are carried forward unchanged from `KN-LIT-13a01d`.
This task **did not fetch either record** and asserts nothing about what the DOI
resolves to; the observation is about the two recorded strings, not about the
world. Reconciling them needs a retrieval and is a `/curate-knowledge` job.
