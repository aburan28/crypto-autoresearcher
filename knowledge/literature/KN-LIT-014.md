---
id: KN-LIT-014
type: literature
title: The number of roots of a system of equations (Bernstein / BKK bound)
authors: [Bernstein David N.]
year: 1975
venue: Functional Analysis and its Applications, 9(3):183-185 (transl. of Funktsional. Anal. i Prilozhen. 9(3):1-4)
identifiers:
  eprint: null
  doi: 10.1007/BF01075595
  url: https://link.springer.com/article/10.1007/BF01075595
tags: [bkk, mixed-volume, newton-polytope, sparse-elimination, bezout, root-counting, complexity]
confidence: established
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Proves that a generic system of n Laurent polynomials in n variables with
prescribed Newton polytopes P_1,...,P_n has exactly MV(P_1,...,P_n) isolated
common solutions in the algebraic torus (C*)^n, where MV is the *mixed volume*
of the polytopes. This is the "B" of the Bernstein-Kushnirenko-Khovanskii (BKK)
theorem and the foundation of support-aware (sparse) root counting.

## Key claims (as reported)
- The mixed-volume count is generically exact and, for sparse systems, is
  typically far below the Bezout number (product of total degrees), since it
  depends on the actual monomial support, not on total degree.
- Companion results: Kushnirenko, "Newton polytopes and the Bezout theorem,"
  Funct. Anal. Appl. 10(3):233-235, 1976 (doi:10.1007/BF01075534) -- the
  unmixed case, count n!*Vol(P) for a common polytope P; and Khovanskii,
  "Newton polyhedra and the genus of complete intersections," Funct. Anal.
  Appl. 12(1):38-46, 1978 (doi:10.1007/BF01077562) -- the toric-geometry
  backbone.

## Relevance to this program
The theoretical basis of the program's BKK cluster (RQ-BKK-001, RQ-BKKMV-001,
KN-OPEN-004). Semaev summation polynomials (KN-TECH-002) are sparse: if their
Newton polytopes are proper subpolytopes of the degree box, MV < Bezout and
support-aware elimination could undercut the dense composed-resultant cost the
program measured (exponent ~1.979). Whether the Semaev polytopes are saturated
(MV = Bezout, method dies) is exactly the decidable stage-0 question of
RQ-BKK-001.

## Not verified here
Full paper not read; the mixed-volume theorem is textbook-level and
reconstructible (hence confidence: established). Bibliographic fields (incl. the
Kushnirenko/Khovanskii companions) confirmed against publisher DOI / Math-Net.Ru
records via search, not by fetching the primary pages.
