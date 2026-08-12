---
id: KN-LIT-13a01d
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
tags: [code-based, mceliece, structural-attack, key-recovery, distinguisher, high-rate, goppa, algebraic-cryptanalysis, foundational]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**A distinguisher for high-rate McEliece cryptosystems** — the paper that
broke the long-standing belief that Goppa codes were indistinguishable from
random codes. It does not recover keys; it distinguishes, in the high-rate
regime, and that was enough to unsettle a foundational assumption.

## Key claims (as reported)
- High-rate Goppa/alternant public keys are distinguishable from random.
- A **distinguisher**, not a key-recovery attack — the separation is explicit.
- Confined to high rate.

## Relevance to this program
The origin of the modern structural line and, for this program, an important
case study in **what a distinguisher is worth.** It did not break McEliece. It
did invalidate a security-reduction step that had been treated as safe, and it
opened the research direction that produced [[KN-LIT-71d1a0]],
[[KN-LIT-4c8135]] and [[KN-LIT-2127]] fifteen years later.

Two disciplines follow. Report a distinguisher as a distinguisher — this
program's claim tiers (`docs/claims-and-verification.md`) forbid promoting it
to a break. And take a distinguisher seriously anyway, because the assumption
it refutes may be load-bearing elsewhere.

The high-rate scoping repeats the pattern of [[KN-LIT-4c8135]]: real result,
bounded regime, and the bound is the practically decisive part.

## Not verified here
Citation verified against the IACR ePrint record for report 2010/331 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1109/itw.2011.6089437).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The rate threshold and the distinguisher's mechanism are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
