---
id: KN-LIT-7567
type: literature
title: A method for finding codewords of small weight
authors: [Stern Jacques]
year: 1989
venue: Coding Theory and Applications, LNCS 388, Springer, pp. 106-113
identifiers:
  eprint: null
  doi: 10.1007/BFb0019850
  url: https://doi.org/10.1007/BFb0019850
tags: [code-based, information-set-decoding, isd, birthday, meet-in-the-middle, cryptanalysis, foundational]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
Adds a birthday/collision step inside the information-set loop: rather than
requiring the information set to be entirely error-free, allow a small number of
errors and find them by a sort-and-match over two halves. This is the structural
idea -- trade memory for a smaller exponent via meet-in-the-middle inside each
iteration -- that every later ISD improvement (MMT, BJMM, nearest-neighbour
variants) generalizes.

## Key claims (as reported)
- Reported asymptotic runtime O~(2^{0.05563n}) for half-distance decoding of a
  random binary linear code at the worst rate.
- Remained the asymptotically best known decoder for random linear codes for
  roughly two decades.

## Relevance to this program
Stern's algorithm is the first point on the exponent curve of KN-TECH-057 where
memory becomes load-bearing, which is why code-based cost claims must be
memory-charged exactly as lattice sieving claims are (KN-TECH-035, KN-TECH-044).
An ISD speedup quoted without its memory term is the same mis-charge this
program already polices in the lattice setting.

## Not verified here
Primary paper not fetched. Author, title, venue (LNCS 388), pages, and year
confirmed via search against DBLP and the Springer DOI. The 0.05563 exponent is
relayed from secondary sources quoting the result.
