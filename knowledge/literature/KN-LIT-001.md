---
id: KN-LIT-001
type: literature
title: Summation polynomials and the discrete logarithm problem on elliptic curves
authors: [Semaev Igor]
year: 2004
venue: IACR Cryptology ePrint Archive
identifiers:
  eprint: iacr:2004/031
  doi: null
  url: https://eprint.iacr.org/2004/031
tags: [semaev, summation-polynomial, index-calculus, point-decomposition, ecdlp, foundational]
confidence: reported
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Introduces the family of *summation polynomials* S_n for an elliptic curve.
S_n(x_1,...,x_n) vanishes exactly when there exist points P_i with the given
x-coordinates summing to the identity. Proposes using them to build an
index-calculus-style algorithm for ECDLP by decomposing points over a factor
base of small-x-coordinate points.

## Key claims (as reported)
- S_2(x1,x2) = x1 - x2; S_3 is explicit (degree 2 in each variable); higher
  S_n are built by resultants: S_n = Res_x(S_{n-k+1}, S_{k+1}).
- deg of S_n in each variable is 2^{n-2}; the decomposition test reduces to
  solving a polynomial system whose difficulty is the crux of the method.
- Framed as a program/algorithm, not a proven subexponential result over
  prime fields.

## Relevance to this program
Foundational. Any proposal to "use summation polynomials for decomposition"
is `known` at the mechanism level — novelty must live in the *representation,
factor-base, elimination, or solving* strategy, not the idea itself. Defines
the objects EXP-SEMAEV-* measure.

## Not verified here
Full PDF not read; degree/complexity statements relayed from the abstract and
secondary sources, not re-derived.
