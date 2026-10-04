---
id: KN-LIT-fa389d
type: literature
title: "Weak Fields for ECC"
authors:
  - "Alfred Menezes"
  - "Edlyn Teske"
  - "Annegret Weng"
year: 2004
venue: "LNCS (2004), pp. 366-386; ePrint 2003/128"
identifiers:
  eprint: "iacr:2003/128"
  arxiv: null
  doi: "10.1007/978-3-540-24660-2_28"
  url: null
tags: [index-calculus, weil-descent, ghs, weak-fields, binary-field, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Shows some fields, e.g. GF(2^210), are "weak": every ECDLP over them is solvable much faster than rho on the hardest instances, via GHS Weil descent. Companion: Menezes-Teske, "Cryptographic implications of Hess' generalized GHS attack", AAECC 16:439-460 (2005), doi:10.1007/s00200-005-0186-8 (ePrint 2004/235), which finds char-2 GF(q^5) weak and GF(q^7) partially weak. The binary-field context for why standards use prime n (sect113r1/r2, ECC2-131 use n = 113, 131).

## Key claims (as reported)

- GF(2^210) weak; char-2 GF(q^5) weak; GF(q^7) partially weak (curves with 4 | #E).

## Relevance to this program

Which binary fields are weak under GHS Weil descent. Context for the ECC2K-130 volcano/descendants hardness checks (none GHS-weak).

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
