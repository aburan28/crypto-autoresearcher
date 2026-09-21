---
id: KN-LIT-004
type: literature
title: Using symmetries in the index calculus for elliptic curves discrete logarithm
authors: [Faugere Jean-Charles, Gaudry Pierrick, Huot Louise, Renault Guenael]
year: 2014
venue: Journal of Cryptology, 27(4):595-635
identifiers:
  eprint: null
  doi: 10.1007/s00145-013-9158-5
  url: https://hal.science/hal-00700555/
tags: [symmetry, summation-polynomial, groebner, representation, edwards, index-calculus, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Exploits symmetries of summation polynomials (point negation, and extra
automorphisms on Edwards / twisted Jacobi-intersection curves) to shrink the
polynomial systems solved during point decomposition, speeding the Gröbner
step.

## Key claims (as reported)
- Symmetry group action lets one work with symmetric functions, gaining an
  exponential factor ~2^{omega(n-1)} in the decomposition-solving cost for
  curves admitting the relevant symmetries.
- Curve *model/representation* (Edwards, twisted forms) materially affects the
  achievable speedup.

## Relevance to this program
Direct prior art for the ROADMAP "representation search" program: it already
establishes that coordinate model and symmetry change solving cost. A
representation proposal is `adaptation`, not novel, unless it goes beyond the
symmetries/models treated here. Motivates measuring solving degree vs. model.

## Not verified here
Full paper not read; the exponent of the claimed speedup relayed from
abstract/secondary sources.
