---
id: KN-LIT-023
type: literature
title: Improving the Complexity of Index Calculus Algorithms in Elliptic Curves over Binary Fields
authors: [Faugere Jean-Charles, Perret Ludovic, Petit Christophe, Renault Guenael]
year: 2012
venue: EUROCRYPT 2012, LNCS 7237, pp. 27-44
identifiers:
  eprint: null
  doi: 10.1007/978-3-642-29011-4_4
  url: https://inria.hal.science/hal-00776066
tags: [fppr, index-calculus, binary-field, groebner, first-fall-degree, multi-homogeneous, subexponential, ecdlp, complexity]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Studies the point-decomposition step of Semaev/Gaudry/Diem index calculus for
ECDLP over binary fields F_{2^n}, casting decomposition over the factor base as
a multivariate polynomial system solved by Grobner bases. Exploiting the
multi-homogeneous (symmetric) structure yields a refined complexity analysis and
a subexponential-flavored algorithm.

## Key claims (as reported)
- Solves ECDLP over any F_{2^n} in time O(2^{omega*t}) with t ~ n/2 -- an
  improvement over generic square-root attacks in that regime.
- Explicitly CONDITIONAL on a heuristic *first-fall-degree* assumption governing
  the Grobner solving degree; the complexity is presented as heuristic.

## Relevance to this program
Source of the first-fall-degree assumption underlying subexponential-flavored
binary-field claims, and the object the program's Grobner experiments measure
(KN-TECH-004, KN-OPEN-002). Scope is strictly *binary fields*; whether the
first-fall-degree heuristic and this complexity transfer to prime fields is open
(KN-OPEN-002). Closely related to the Weil-descent polynomial-system analysis of
Petit-Quisquater (KN-LIT-005). A prime-field first-fall-degree measurement is a
legitimate, non-duplicative experiment.

## Not verified here
Full paper not read; the complexity exponent and first-fall-degree assumption
relayed as the paper's stated heuristics. No IACR ePrint located; open preprint
is HAL hal-00776066. Fields confirmed against publisher / HAL records via search,
not by fetching the primary pages.
