---
id: KN-LIT-027
type: literature
title: A new efficient algorithm for computing Grobner bases (F4)
authors: [Faugere Jean-Charles]
year: 1999
venue: Journal of Pure and Applied Algebra, 139(1-3):61-88
identifiers:
  eprint: null
  doi: 10.1016/S0022-4049(99)00005-5
  url: https://www.sciencedirect.com/science/article/pii/S0022404999000055
tags: [groebner-basis, f4, faugere, macaulay-matrix, sparse-linear-algebra, solving, point-decomposition]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
F4 keeps Buchberger's S-polynomial framework (KN-LIT-026) but replaces
one-at-a-time reduction with *simultaneous* reduction of many S-polynomials via
sparse linear algebra: a symbolic precomputation collects all monomials of a
degree step into a Macaulay-style matrix, and Gaussian elimination row-reduces
it. Successive truncated Grobner bases are computed degree by degree.

## Key claims (as reported)
- Recasting reduction as sparse row reduction of structured matrices gives large
  speedups; solved previously intractable benchmarks (e.g. Cyclic-9).
- The degree-by-degree Macaulay-matrix view descends from Lazard, "Grobner
  bases, Gaussian elimination and resolution of systems of algebraic equations,"
  EUROCAL 1983, LNCS 162:146-156 (doi:10.1007/3-540-12868-9_99).

## Relevance to this program
The practical engine for solving Semaev decomposition systems (KN-TECH-002,
KN-TECH-004). Its degree-by-degree matrix structure is exactly what the
solving-degree / degree-of-regularity complexity analysis (KN-LIT-029)
measures, and it is the point where sparse-elimination (BKK, KN-TECH-007) and
sparse linear algebra (KN-TECH-008) could in principle reduce the dominant cost
of point decomposition (KN-OPEN-002, KN-OPEN-004).

## Not verified here
Full paper not read; the matrix-F4 reformulation is textbook-level in computer
algebra (hence confidence: established). Bibliographic fields (incl. Lazard)
confirmed against the JPAA/Elsevier and Springer DOI records via search, not by
fetching the primary pages.
