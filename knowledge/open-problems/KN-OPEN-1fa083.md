---
id: KN-OPEN-1fa083
type: open_problem
title: >-
  Sub-MITM restricted-root oracles for prime-field point decomposition: compute the m-fold norm
  of S_{m+1} over an interval or subgroup grid in B^{1-eps} (m = 4), or find small roots of S_5
  at delta ~ 1/5 -- the two precise problems whose solution would move the prime-field
  index-calculus exponent
tags: [prime-field, ecdlp, index-calculus, point-decomposition, summation-polynomial, restricted-root, norm, baby-step-giant-step, coppersmith, open]
confidence: reported
status: open
source_refs: [KN-LIT-9c442f, KN-LIT-8bf122, KN-LIT-ed7e23, KN-LIT-8aca31, KN-LIT-ad6582, KN-LIT-001, KN-OPEN-020, KR-IC-76aaed, KR-IC-3845fa, DEC-20261025-48232f]
added: 2026-10-25
superseded_by: null
---

## Statement

Let `E/F_p` have prime order, `S_{m+1}` Semaev's summation polynomial (degree
`2^{m−1}` in each variable), and `V ⊂ F_p` a base of size `B ≈ p^{1/m}` that
is either an interval `[0, B)` or a multiplicative subgroup `μ_B` (`B | p−1`).
The decomposition oracle must decide, for a target `z = x(R)`, whether
`(x_1,…,x_m) ∈ V^m` with `S_{m+1}(x, z) = 0` exists, and find it.

With the index-calculus accounting `cost(B) ≈ (m!/2^m)·p·T_dec/B^{m−1} + m·B²`
(optimum `B = (p·T_dec)^{1/(m+1)}`, total `≈ (p·T_dec)^{2/(m+1)}`), `m = 2`
never beats `√p`, `m = 3` ties only with `T_dec = O(1)`, and the first arity
that can win is `m = 4`, which needs `T_dec ≪ p^{1/4} = B`. PKM's form of the
same threshold is "solve one system in time below `p^{1/2−1/m}`".

**P1 (multidimensional structured norm).** Compute
`N_V(z) = ∏_{u ∈ V^4} S_5(u_1,u_2,u_3,u_4, z) mod p` in time `B^{1−ε}·polylog p`
for `V = [0,B)` or `V = μ_B`. One-dimensional products are sublinear
(Bostan–Gaudry–Schost `Õ(√B)` for intervals; `Res(g, X^B − 1)` in `Õ(log B)`
for subgroups), but every known reduction of the two-dimensional product
`∏_{(u,v)∈V²} S_3(u,v,z)` costs `≥ Õ(B)` (subgroup) or `Õ(B^{3/2})`–`B^{4/3}`
(interval), and the four-fold norm `≥ Õ(B³)` versus the MITM table's `B²`.

**P2 (small roots at the decomposition threshold).** Find the roots of
`S_5(x_1..x_4, z) ≡ 0 (mod p)` with `|x_i| < p^{1/5}` in time `≪ p^{1/4}`.
The Jochemsz–May basic-strategy reach is `δ_max = 1/80` and the fixed-target
support of `S_5` is the full box (6561 of 6561 monomials), so no
polytope-aware basic construction helps; any solution must use the curve
structure of the instances (the roots are x-coordinates of points whose sum
is fixed), not the polynomial's shape. Provably optimal shift sets (Ryan,
EUROCRYPT 2025) are the one unexamined lattice variant
(LEAD-ICP-coppersmith-smallroot-semaev).

## What is known

- Both problems sit exactly where the counting literature is silent or
  negative: a degree-`d` curve has `≪ d^{4/3}|H|^{2/3}` points in `H × H`
  (Corvaja–Zannier, as reported); a cubic has `M^{1/3+o(1)}` points in an
  `M × M` box for `M < p^{1/8}`, and the range `p^{1/3} < M < p^{1/2}` is
  explicitly open (Chang–Cilleruelo–Garaev–Hernández–Shparlinski–Zumalacárregui,
  as reported). None of these gives a finding algorithm.
- The only sub-linear algorithms in a subgroup setting are
  Bourgain–Garaev–Konyagin–Shparlinski's identity tests for the hidden
  shifted power problem (`e^{1/4+o(1)}`, `e^{2/3+o(1)}`, as reported); they
  rely on a rigid `(x+s)^e` structure and additive-combinatorial product-set
  estimates and do not transfer to `S_{m+1} = 0`.
- Negative data: `Ψ_2(z) = ∏_{u≠v∈V} S_3(u,v,z)` is dense (8034–8065 of 8065
  coefficients) for both base types at `p = 65537`, `B = 64`; the linear-`f`
  collapse through cyclotomic numbers costs `≥ p/B`.
- Relation to KN-OPEN-020: that problem asks for a universal no-go for
  algebraically described bases; this one asks for the algorithm on the two
  specific structured bases that the no-go arguments (KR-IC-585a96 for
  algebra, KR-IC-76aaed for size) do not reach because they concern the
  *solver*, not the base.

## What would decide it

A positive answer to P1 at `m = 4` gives a prime-field index calculus below
`√p` by the accounting above and must therefore be checked against Wagner's
Theorem 2 (it must read coordinates non-generically) and against the
Yokoyama et al. floor (it must not be an S-polynomial Groebner computation).
A proof that the four-fold norm needs `Ω(B²)` in a stated algebraic model
closes the product paradigm the way Yokoyama et al. closed the Groebner one.

## Provenance

Formulated in the 2026-10-24 review recorded in DEC-20261025-48232f
(`docs/reports/aps-prime-field-review-20261025/report.md` §4.1).
