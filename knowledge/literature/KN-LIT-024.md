---
id: KN-LIT-024
type: literature
title: On the First Fall Degree of Summation Polynomials
authors: [Kousidis Stavros, Wiemers Andreas]
year: 2019
venue: Journal of Mathematical Cryptology, 13(3-4):229-237 (ePrint 2015)
identifiers:
  eprint: iacr:2015/1121
  doi: null
  arxiv: "1906.05594"
  url: https://eprint.iacr.org/2015/1121
tags: [kousidis-wiemers, first-fall-degree, summation-polynomial, groebner, weil-descent, binary-field, ecdlp, complexity]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Studies the *first-fall degree* of the polynomial systems from Weil descent
along Semaev summation polynomials -- the quantity controlling Grobner-basis
complexity in binary-field index calculus. Rigorously improves the
Petit-Quisquater bound.

## Key claims (as reported)
- Proves a degree fall provably occurs at degree m^2 - m + 1 (improving the
  earlier m^2 + 1 bound), established by exhibiting the top-degree homogeneous
  part of the system -- so the first-fall degree grows only polynomially (~m^2).
- Broadly SUPPORTIVE of the first-fall-degree picture the FPPR heuristics rely
  on (KN-LIT-023). IMPORTANT distinction: they establish the value of the
  first-fall degree itself, NOT the separate, more contentious heuristic that
  first-fall degree tracks the degree of regularity.

## Relevance to this program
Direct, rigorous evidence on the first-fall-degree quantity the program measures
(KN-TECH-004, KN-OPEN-002). Use it to separate what is *proven* (the first-fall
bound) from what is still *assumed* (first-fall = degree of regularity) when
interpreting Grobner cost trends -- exactly the gap KN-OPEN-002 flags over prime
fields.

## Not verified here
Full paper not read; the m^2 - m + 1 bound and the proven-vs-assumed distinction
relayed from the ePrint abstract and secondary sources. The De Gruyter JMC DOI
could not be confirmed and is omitted; identifiers are IACR ePrint 2015/1121 and
arXiv:1906.05594. Fields confirmed via search, not by fetching the primary pages.
