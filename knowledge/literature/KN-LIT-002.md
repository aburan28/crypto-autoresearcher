---
id: KN-LIT-002
type: literature
title: Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem
authors: [Gaudry Pierrick]
year: 2009
venue: Journal of Symbolic Computation, 44(12):1690-1702
identifiers:
  eprint: iacr:2004/073
  doi: 10.1016/j.jsc.2008.08.005
  url: https://www.sciencedirect.com/science/article/pii/S074771710800182X
tags: [gaudry, index-calculus, point-decomposition, weil-restriction, extension-field, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Index-calculus algorithm for discrete logs on abelian varieties of small
dimension, applied via Weil restriction to elliptic/hyperelliptic curves over
small-degree extension fields, without embedding into a curve Jacobian. The
point-decomposition relations are found by solving polynomial systems.

## Key claims (as reported)
- Heuristic asymptotic time O~(q^{4/3}) for ECDLP over GF(q^3); O~(q^{3/2})
  over GF(q^4) or genus-2 over GF(q^2).
- Establishes the point-decomposition-over-a-factor-base framework that
  summation-polynomial ECDLP attacks instantiate.

## Relevance to this program
Defines the extension-field regime where index calculus provably beats rho.
Sharp contrast to the **prime-field** regime (see KN-OPEN-001) where no such
advantage is known. Any prime-field claim must not silently borrow
extension-field asymptotics.

## Not verified here
Full PDF not read; asymptotic exponents relayed from abstract/secondary
sources.
