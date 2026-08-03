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
