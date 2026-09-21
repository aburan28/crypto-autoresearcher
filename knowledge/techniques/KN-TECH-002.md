---
id: KN-TECH-002
type: technique
title: Semaev summation polynomials
tags: [semaev, summation-polynomial, point-decomposition, index-calculus]
confidence: established
complexity: deg of S_n in each variable is 2^{n-2}; construction by iterated resultants
applicability: elliptic curves in short Weierstrass form (and, via change of model, other forms)
source_refs: [KN-LIT-001, KN-LIT-004]
added: 2026-07-19
superseded_by: null
---

## Definition
For E/F_q, the n-th summation polynomial S_n(x_1,...,x_n) in F_q[x_1,...,x_n]
vanishes iff there exist points P_i = (x_i, y_i) on E (over the algebraic
closure) with P_1 + ... + P_n = O.

- S_2(x1, x2) = x1 - x2.
- S_3(x1, x2, x3) for y^2 = x^3 + a*x + b:
  (x1 - x2)^2 * x3^2  - 2*((x1 + x2)*(x1*x2 + a) + 2*b) * x3
  + ((x1*x2 - a)^2 - 4*b*(x1 + x2)).
- Recurrence: S_n(x_1,...,x_n) = Res_x( S_{n-k+1}(x_1,...,x_{n-k}, x),
  S_{k+1}(x_{n-k+1},...,x_n, x) ) for 2 <= k <= n-2.

## Role in index calculus
To decompose a point R over a factor base F (points with x in a chosen set V),
seek x_1,...,x_m in V with S_{m+1}(x_1,...,x_m, x(R)) = 0, i.e. R equals a sum
of m factor-base points (up to signs). The decomposition test is a polynomial
system solved by Gröbner methods (KN-TECH-004). Degrees 2^{n-2} make large n
expensive -- the core bottleneck.

## Notes
Symmetry of S_n under coordinate permutation and point negation is exploited
to reduce solving cost (KN-LIT-004). Implemented in the harness (harness/semaev.py).
