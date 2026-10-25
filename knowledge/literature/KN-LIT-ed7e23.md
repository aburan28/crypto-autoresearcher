---
id: KN-LIT-ed7e23
type: literature
title: "Linear recurrences with polynomial coefficients and application to integer factorization and Cartier-Manin operator: the N-th term of a P-recursive sequence, hence prod_{i<N} M(i) for a polynomial matrix M, in O~(sqrt N) ring operations (baby-step/giant-step)"
authors:
  - "Alin Bostan"
  - "Pierrick Gaudry"
  - "Eric Schost"
year: 2007
venue: "SIAM Journal on Computing 36(6):1777-1806"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1137/S0097539704443793"
  url: "https://cs.uwaterloo.ca/~eschost/publications/cartier.pdf"
tags: [fast-algorithms, baby-step-giant-step, factorial, p-recursive, strassen, point-counting, cartier-manin]
confidence: reported
citation_verified: web
added: "2026-10-25"
superseded_by: null
---

## Contribution

Improves the Chudnovsky–Chudnovsky / Strassen baby-step/giant-step technique
for computing the N-th term of a linear recurrence with polynomial
coefficients, hence products `∏_{i<N} M(i)` of polynomial matrices (and
`N! mod p`), in `Õ(√N)` ring operations, with applications to integer
factorization (Pollard–Strassen) and to the Cartier–Manin operator for
point counting on hyperelliptic curves.

## Key claims (as reported)

- Main result: the N-th term of a P-recursive sequence in `O(M(√N) log N)`
  (or `Õ(√N)`) ring operations, improving the previous `Õ(√N)`-with-larger-
  log-factors bounds; space `O(√N)`.
- Costa–Gerbicz–Harvey (arXiv:1209.3436) restate it as the best single-prime
  bound for `(p−1)! mod p^2` ("essentially due to Strassen", improvable by a
  log factor via Bostan–Gaudry–Schost).

## Relevance to this program

The one-dimensional case of the product/norm formulation of the prime-field
point decomposition problem: for an interval base `V = [0, B)` the product
`∏_{u<B} g(u)` of a fixed low-degree polynomial costs `Õ(√B · deg g)`, so the
last variable of a decomposition costs `√B` instead of `B`. The
multidimensional products a breakthrough would need (`∏_{u ∈ [0,B)^4}
S_5(u, z)` in `B^{1−ε}`) have no known analogue; see `KR-IC-3845fa` and
`KN-OPEN-1fa083`.

## Not verified here

The paper itself was not read in this session; the statement is relayed from
the abstract and from Costa–Gerbicz–Harvey's restatement. Confidence
`reported`.

## Provenance

Identified and relayed on 2026-10-24 by a delegated literature lane of the
session recorded in DEC-20261025-48232f.
