---
id: KN-LIT-f37b9a
type: literature
title: "The complexity of solving Weil restriction systems"
authors:
  - "Caminata, Alessio"
  - "Ceria, Michela"
  - "Gorla, Elisa"
year: 2023
venue: "arXiv:2112.10506v2 (3 Feb 2023); submitted 2021"
identifiers:
  eprint: null
  doi: null
  arxiv: "2112.10506"
  url: "https://arxiv.org/abs/2112.10506"
tags: [weil-restriction, weil-descent, solving-degree, degree-of-regularity,
  castelnuovo-mumford, groebner, growth-law, index-calculus, ecdlp,
  summation-polynomial, prior-art, body-read]
confidence: high
citation_verified: web
citation_provenance: retrieved
body_read: true
added: "2026-09-16"
superseded_by: null
---

## Why this entry matters to this program

**It gives a proven growth law in the descent parameter `n`** — the quantity
`RQ-DREG-bd6c86` asks about, and the quantity the originating slide says is not
understood. The full text was read on 2026-09-16.

## Setting

Weil restriction of scalars for a finite Galois extension `k ↪ K` of degree `n`
sends a system `F` over `K` to `Weil(F)` over `k` in `nm` variables, with
solutions in natural bijection. This is exactly the construction that turns a
summation-polynomial system over `F_{q^n}` into the descended system over `F_q`.

## Main results used here

- **Cor. 3.4(2) / Prop. 4.13.** If `(F^top)_d = R_d` for `d ≫ 0`, then
  **`d_reg(Weil(F)) = n · d_reg(F) − n + 1`** — an **exact formula**, linear in
  `n` with slope `d_reg(F) − 1`. Also `Weil(F^top) = Weil(F)^top`.
- **Cor. 3.4(1).** `Weil(F)` in generic coordinates over `k` ⟹ `sd(Weil(F)) ≤ n·reg(F) − n + 1`.
- **Cor. 4.9.** `F ⊆ F_{q^n}[x]` containing the field equations of `F_{q^n}`, and `t ∤ 0` in `R[t]/(F^h)` ⟹ `sd(Weil(F)) ≤ n·reg(F^h) − n + 1`.
- **Cor. 4.12.** Same hypotheses ⟹ `sd(Weil(F) ∪ {x_{i,j}^q − x_{i,j}}) ≤ n·reg(F^h) − n + 1`. This is the bound for the system one actually solves, with the `F_q` field equations adjoined.
- **Cor. 4.10.** Complete-intersection case: the bound is `n(d_1 + … + d_r) − nr + 1`.

## Consequence for the ECDLP question, stated carefully

For the summation polynomial `S_{m+1}`, the pre-descent invariants depend on `m`
and **not** on `n`. So the growth of `d_reg` along the descent parameter is
**linear in `n` with an `n`-independent slope**, and by Cor. 4.12 the solving
degree of the descended system with field equations is bounded by
`n·reg(F^h) − n + 1`.

**This is an upper bound and it is not subexponential.** Solving degree linear
in `n` gives Gröbner cost roughly `(mn')^{ω·Θ(n)}`. The first-fall-degree
assumption claims far more: that the true solving degree is essentially
*bounded*. The open problem is exactly the gap between a proven linear upper
bound and a conjectured constant — which is a much sharper statement of the
slide's question than "slower than random".

## Not verified here

- **Summation polynomials and ECDLP are not named** in the paper's abstract; the application to Semaev systems is this program's, not the authors'.
- The hypotheses **`t ∤ 0` modulo `F^h`** and **generic coordinates over `k`** are real and have **not** been checked for any Semaev descent system.
- Prop. 4.13 is stated for `Weil(F)` **before** adjoining the `F_q` field equations. Adjoining them can only lower `d_reg`, so the formula is an upper estimate for the practical system — but the exact statement is about `Weil(F)` and the distinction must not be dropped.
- `reg(F^h)` for the summation systems has not been computed here; the claim that it is `n`-independent follows from `S_{m+1}` not depending on `n`, and has not been verified against a concrete system.
