---
id: KN-LIT-891
type: literature
title: "Multiradical isogenies"
authors:
  - "Wouter Castryck"
  - "Thomas Decru"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1133"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1133"
tags: [abelian-variety, elliptic-curve, finite-field, hash, isogeny, jacobian, protocol, provable-security, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We argue that for all integers N ≥ 2 and g ≥ 1 there exist “multiradical” isogeny formulae, that can be iteratively applied to compute (N k , . . . , N k )-isogenies between principally polarized g-dimensional abelian varieties, for any value of k ≥ 2. The formulae are complete: each iteration involves the extraction of g(g + 1)/2 different N th roots, whence the epithet multiradical, and by varying which roots are chosen one computes all N g(g+1)/2 extensions to an (N k , . . . , N k )-isogeny of the incoming (N k−1 , . . . , N k−1 )-isogeny.

## Key claims (as reported)
- Our group-theoretic argumentation is heuristic, but it is supported by concrete formulae for several prominent families.
- As our main application, we illustrate the use of multiradical isogenies by implementing a hash function from (3, 3)-isogenies between Jacobians of superspecial genus-2 curves, showing that it outperforms its (2, 2)-counterpart by an asymptotic factor ≈ 9 in terms of speed.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1133.pdf`
