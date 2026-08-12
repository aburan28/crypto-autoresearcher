---
id: KN-LIT-029
type: literature
title: On the complexity of Grobner basis computation of semi-regular overdetermined algebraic equations
authors: [Bardet Magali, Faugere Jean-Charles, Salvy Bruno]
year: 2004
venue: Proc. ICPSS 2004 (Int. Conf. on Polynomial System Solving), Paris, pp. 71-75
identifiers:
  eprint: null
  doi: null
  url: http://magali.bardet.free.fr/Publis/ltx43BF.pdf
tags: [degree-of-regularity, semi-regular, groebner-complexity, solving-degree, hilbert-series, point-decomposition, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Extends the notion of regular sequence to overdetermined systems via
*semi-regular* sequences and shows the cost of a Grobner-basis computation
(e.g. by F5, KN-LIT-028) is governed by the *degree of regularity* -- the
highest degree reached during the computation. For semi-regular systems this
degree is predictable from the Hilbert series, giving sharp asymptotic
complexity bounds.

## Key claims (as reported)
- Semi-regular systems have a degree of regularity computable from the Hilbert
  series -> explicit Grobner complexity estimates.
- IMPORTANT hedge: identifying the degree of regularity with the observed
  *first-fall degree* (or solving degree) is a HEURISTIC, not a theorem, and the
  semi-regularity assumption need not hold for structured systems.
- Related citable forms: Bardet PhD thesis (Univ. Paris VI, 2004);
  Bardet-Faugere-Salvy-Yang (MEGA 2005).

## Relevance to this program
The complexity backbone of the algebraic ECDLP index-calculus argument
(KN-OPEN-002): subexponential-flavored point-decomposition claims (KN-LIT-023,
KN-LIT-025) hinge on assuming Semaev systems are semi-regular so their degree of
regularity is bounded. The contested first-fall vs degree-of-regularity gap is
exactly what this framework leaves open, and what Kousidis-Wiemers (KN-LIT-024)
partially resolves (they prove the first-fall value, NOT the identification with
degree of regularity). A prime-field measurement of whether Semaev systems are
semi-regular is a legitimate experiment.

## Not verified here
Full paper not read; the semi-regularity framework and the heuristic caveat
relayed from the abstract and standard secondary sources (hence confidence:
reported). No registered DOI located for the ICPSS 2004 proceedings item
(author-hosted PDF is the primary link); other fields confirmed via search.
