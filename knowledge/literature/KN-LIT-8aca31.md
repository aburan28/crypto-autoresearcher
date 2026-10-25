---
id: KN-LIT-8aca31
type: literature
title: "A strategy for finding roots of multivariate polynomials with new applications in attacking RSA variants (full text read): basic and extended Coppersmith strategies, their determinant conditions, Assumption 1, and the generalized-rectangle bound prod X_i^{lambda_i} < N^{2/((n+1)D)}"
authors:
  - "Ellen Jochemsz"
  - "Alexander May"
year: 2006
venue: "ASIACRYPT 2006, LNCS 4284, pp. 267-282"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/11935230_18"
  url: "https://www.iacr.org/archive/asiacrypt2006/42840270/42840270.pdf"
tags: [coppersmith, lattice, small-roots, multivariate, jochemsz-may, newton-polytope, rsa]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

A general recipe for Coppersmith-type lattices for one modular or integer
multivariate polynomial, with the determinant condition stated in terms of
the monomial sets of `f^m`, and an appendix that recovers the known
shape-specific bounds. Supersedes the bulk stub KN-LIT-2244 (abstract only).

## Key claims (verified from the full text, Wayback copy)

- §2.1 Lemma 1 (Howgrave-Graham, n variables): if `h` has at most `ω`
  monomials, `h(x^{(0)}) ≡ 0 mod N` with `|x_i^{(0)}| < X_i`, and
  `‖h(x_1X_1,…,x_nX_n)‖ < N/√ω`, then `h(x^{(0)}) = 0` over `Z`.
- §2.2 basic strategy (modular): monomial sets `M_k := {monomials of f_N^m
  whose quotient by l^k is a monomial of f_N^{m−k}}` (`l` the leading
  monomial), shifts `g = (x^i/l^k)·f_N^k·N^{m−k}`; the determinant condition
  reduces to `∏_{j} X_j^{s_j} < N^{s_N}` with `s_j = Σ_{x^i ∈ M_0} i_j` and
  `s_N = Σ_{k=1}^{m} |M_k|` (their condition (1)); integer version `∏ X_j^{s_j}
  < W^{s_W}` (condition (2)). "Assumption 1: The resultant computations for
  the polynomials h_i yield non-zero polynomials." The extended strategy adds
  extra shifts `x_1^j`, `0 ≤ j ≤ t = τm`. (HEURISTIC for ≥ 2 variables.)
- Appendix A (modular shapes): "Generalized Rectangle ... the degree of x_i is
  λ_iD. The bound `X_1^{λ_1}⋯X_n^{λ_n} < N^{2/((n+1)D)}` can be obtained with
  the basic strategy"; "Generalized Lower Triangle ... `X_1^{λ_1}⋯X_n^{λ_n} <
  N^{1/D}`"; Boneh–Durfee and Blömer–May shapes reproduced. Appendix B gives
  the integer analogues with `W`.
- Later restatement (as reported): Feng–Nitaj–Pan, ePrint 2024/1330, show the
  Jochemsz–May bound equals the leading coefficient of a Hilbert function,
  i.e. the volume of the Newton polytope.

## Relevance to this program

Applied to Semaev's PDP polynomial `S_{m+1}(x_1,…,x_m, x_R)` (degree
`2^{m−1}` in each of `m` variables, generalized rectangle with `D = 2^{m−1}`,
`λ_i = 1`) the bound is `∏ X_i < p^{2/((m+1)2^{m−1})}`, i.e. for equal bounds
`δ_max = 2/(m(m+1)2^{m−1})` = 1/6, 1/24, 1/80, 1/240 for m = 2..5, against
the `∏ X_i ≈ p` the PDP needs. The session recorded in DEC-20261025-48232f
derived the shape-general form `δ_max = 1/((m+1)·c_N)` (`c_N` = coordinate
sum of the Newton-polytope centroid) and verified that the fixed-target
support of `S_3`, `S_4`, `S_5` is the full box, so no polytope-aware strategy
improves on the rectangle bound. See `KR-IC-76aaed` and the measured Probes
B/C in aburan28/crypto `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md`.

## Not verified here

The paper's RSA applications were not read in detail.

## Provenance

Full text (Wayback copy of the IACR archive PDF) read on 2026-10-24 by a
delegated literature lane of the session recorded in DEC-20261025-48232f.
