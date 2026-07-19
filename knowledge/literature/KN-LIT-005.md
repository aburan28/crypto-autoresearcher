---
id: KN-LIT-005
type: literature
title: On polynomial systems arising from a Weil descent
authors: [Petit Christophe, Quisquater Jean-Jacques]
year: 2012
venue: ASIACRYPT 2012, LNCS 7658, pp. 451-466
identifiers:
  eprint: iacr:2012/146
  doi: 10.1007/978-3-642-34961-4_28
  url: https://eprint.iacr.org/2012/146
tags: [petit, weil-descent, groebner, first-fall-degree, degree-of-regularity, binary-field, index-calculus, ecdlp, complexity]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Analyzes the polynomial systems (Faugere-Perret-Petit-Renault systems) arising
from Weil descent of summation-polynomial decomposition, and their Gröbner-basis
solving complexity, driven by the *first-fall degree* heuristic.

## Key claims (as reported)
- Conjectures/experimentally supports that the degree of regularity of these
  systems is only slightly above the equations' degrees, far below generic
  systems -> unexpectedly low solving complexity.
- Heuristic: an index-calculus variant for binary-field ECDLP in
  O(2^{c n^{2/3} log n}) bit operations, c < 2 -> subexponential over GF(2^n).

## Relevance to this program
Defines the key measurable quantity for the program's Gröbner experiments:
*first-fall degree* and *degree of regularity* as functions of parameters.
The claims are heuristic and binary-field; prime-field behavior is a distinct,
open question (KN-OPEN-002). A prime-field first-fall-degree measurement is a
legitimate, non-duplicative experiment.

## Not verified here
Full paper not read; the complexity exponent and degree-of-regularity claims
relayed as the paper's stated heuristics, not reproduced.
