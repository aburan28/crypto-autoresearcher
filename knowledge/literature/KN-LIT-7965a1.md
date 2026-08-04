---
id: KN-LIT-7965a1
type: literature
title: "An algorithmic reduction theory for binary codes: LLL and more"
authors:
  - "Thomas Debris-Alazard"
  - "Léo Ducas"
  - "Wessel P. J. van Woerden"
year: 2022
venue: "IEEE Transactions on Information Theory"
identifiers:
  eprint: "iacr:2020/869"
  doi: "10.1109/tit.2022.3143620"
  arxiv: null
  url: "https://eprint.iacr.org/2020/869"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, lattice-reduction, lll, reduction-theory, cross-domain]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
Builds an **algorithmic reduction theory for binary codes** analogous to lattice
reduction — an LLL for codes. Where lattice reduction produces a basis of
successively shorter, more orthogonal vectors, this constructs the code-theoretic
counterpart, with size-reduction and exchange steps defined for the Hamming
metric.

## Key claims (as reported)
- A reduction theory for binary codes, with an LLL analogue.
- Establishes the structural analogy between lattice bases and code generator matrices as an algorithmic tool, not only a metaphor.

## Relevance to this program
The single most interesting entry in this sweep for this program's *method*,
independent of its subject. It is a worked, published example of the move
`docs/inventor-protocol.md` calls object-first generation: identify the
structure that makes an algorithm work in domain A (basis reduction), find the
object playing that role in domain B, and build the algorithm there.

Two lessons are recorded honestly. The transfer was mathematically successful.
It did **not** break code-based cryptography — the analogue exists and is
weaker in its native setting than LLL is in its own. A successful structural
transfer is therefore evidence about *feasibility of the analogy*, not about
security, and this program must not conflate the two when it attempts the same
move toward the ECDLP.

**Does not bear on the ECDLP directly**, but is the strongest available
template for how to attempt and how to report a cross-domain technique
transfer.

## Not verified here
Citation verified against the IACR ePrint record for report 2020/869 (title and author list checked) on 2026-08-03; citation verified against the Crossref record (DOI 10.1109/tit.2022.3143620).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

The precise reduction guarantees, the algorithm's complexity, and its concrete
performance against ISD are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
