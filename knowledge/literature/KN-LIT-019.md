---
id: KN-LIT-019
type: literature
title: On the number of incidences between points and planes in three dimensions
authors: [Rudnev Misha]
year: 2018
venue: Combinatorica, 38(1):219-254
identifiers:
  eprint: null
  doi: 10.1007/s00493-016-3329-6
  arxiv: "1407.0426"
  url: https://arxiv.org/abs/1407.0426
tags: [incidence-geometry, szemeredi-trotter, finite-field, point-line, rich-lines, relation-harvesting, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-21
superseded_by: null
---

## Contribution
Proves a point-plane incidence bound in projective 3-space over any field of
characteristic != 2 (via the Klein quadric). Through point-plane/point-line
duality it implies a Szemeredi-Trotter-type point-line incidence bound over
F_p, the sharpest general finite-field incidence tool of its kind.

## Key claims (as reported)
- For m points and n planes with m >= n, incidences are O(m*sqrt(n) + k*m),
  where k bounds collinear planes -- a main-term sqrt(n) contribution plus a
  collinearity error term -- valid for n = O(p^2) in characteristic p.
- Sharpened point-line form: Stevens & de Zeeuw, "An improved point-line
  incidence bound over arbitrary fields," Bull. LMS 49(5):842-858, 2017
  (arXiv:1609.06284, doi:10.1112/blms.12077): O(m^{2/3} n^{2/3} + m + n) in a
  balanced range. Baseline expander form: Vinh, Eur. J. Combin. 32(8):1177-1181,
  2011 (doi:10.1016/j.ejc.2011.06.008): |I - |P||L|/p| <= sqrt(p|P||L|).

## Relevance to this program
The counting backbone for the program's incidence-harvesting candidates
(RQ-INC-001, RQ-INCB-001, EXP-INC-001): elliptic-curve chords are a structured
line family, and these bounds control how many collinear (rich-line) relations
can exist among factor-base points, and whether EC chord arrangements sit at the
generic Szemeredi-Trotter ceiling or show a curve-specific excess. Note these are
*counting/existence* bounds; the program's open question is whether an
*algorithmic, output-sensitive reporting* primitive with subquadratic setup
exists (KN-OPEN-005 neighborhood), which these theorems do not by themselves
provide.

## Not verified here
Full paper not read; exact exponents, the characteristic-p range, and the
companion bounds relayed from abstracts and secondary sources. Fields confirmed
against arXiv / publisher records via search, not by fetching the primary pages.
