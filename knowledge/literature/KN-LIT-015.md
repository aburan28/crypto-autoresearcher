---
id: KN-LIT-015
type: literature
title: A polyhedral method for solving sparse polynomial systems
authors: [Huber Birkett, Sturmfels Bernd]
year: 1995
venue: Mathematics of Computation, 64(212):1541-1555
identifiers:
  eprint: null
  doi: 10.1090/S0025-5718-1995-1297471-4
  url: https://www.ams.org/journals/mcom/1995-64-212/S0025-5718-1995-1297471-4/
tags: [polyhedral-homotopy, mixed-volume, bkk, sparse-elimination, mixed-subdivision, solving]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Introduces *polyhedral homotopy continuation*: a numerical method that solves a
sparse polynomial system by tracking exactly MV(P_1,...,P_n) continuation paths
-- one per Bernstein/mixed-volume root (KN-LIT-014) -- rather than the far
larger Bezout number of paths used by total-degree homotopies. This is the
algorithmic realization of Bernstein's theorem.

## Key claims (as reported)
- A generic lifting induces a fine mixed (regular) subdivision of the Newton
  polytopes; each mixed cell gives a binomial start system solved in closed
  form, and the homotopy deforms these to the target system.
- Path count is optimal in the BKK sense (= mixed volume), so sparse systems
  cost far less than under dense homotopy or dense resultants.
- Realized in solvers such as PHCpack (Verschelde, ACM TOMS Algorithm 795,
  25(2):251-276, 1999, doi:10.1145/317275.317286) and HOM4PS.

## Relevance to this program
The concrete solver family the program's BKK candidate (RQ-BKK-001) would use to
solve Semaev decomposition systems at the mixed-volume path count instead of the
dense-degree count. Note the method is numerical (continuation over C); the
program works over F_p, so the *relevant transferable content* is the
mixed-volume path/complexity count and the mixed-subdivision structure, not the
floating-point path tracker itself. Sparse-resultant elimination sized by mixed
volume (Canny-Emiris, AAECC 1993 / J. Symbolic Comput. 20(2):117-149, 1995) is
the exact-arithmetic counterpart.

## Not verified here
Full paper not read; path-count and mixed-subdivision claims relayed from the
abstract and standard references. Bibliographic fields confirmed against the AMS
Math. Comp. record via search, not by fetching the primary page.
