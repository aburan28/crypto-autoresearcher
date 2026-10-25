---
id: KN-LIT-8bf122
type: literature
title: "Complexity bounds on Semaev's naive index calculus method for ECDLP (full text read): Groebner bases of the split-base PDP ideal are an extended Euclidean algorithm over the d^m grid; lower bound m*delta*d^{m-1} per system under two statistical assumptions"
authors:
  - "Kazuhiro Yokoyama"
  - "Masaya Yasuda"
  - "Yasushi Takahashi"
  - "Jun Kogure"
year: 2020
venue: "Journal of Mathematical Cryptology 14(1):460-485 (open access)"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1515/jmc-2019-0029"
  url: null
tags: [index-calculus, prime-field, lower-bound, semaev, groebner, split-factor-base, point-decomposition, ecdlp]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

For the point-decomposition ideal `I_m(a,b) = ⟨S_{m+1}(x_1,…,x_m, x(aP+bQ)),
F(x_1), …, F(x_m)⟩` with `F | x^q − x` of degree `d > δ := 2^{m−1}` (any
split factor base: random, interval, subgroup), the authors show the ideal
has a special structure (Groebner computation = extension of the extended
Euclidean algorithm; the cofactor in `1 = T·S + Σ A_i F(x_i)` is the Lagrange
interpolant over the `d^m` points of `V(⟨F(x_1),…,F(x_m)⟩)`), derive a lower
bound on S-polynomial-based Groebner computation, and conclude that the naive
method cannot beat generic algorithms. Supersedes the abstract-only stub
KN-LIT-d8e1b9 (which superseded the bulk stub KN-LIT-4558).

## Key claims (verified from the full text)

- §2.4 cost model (HEURISTIC, standard): probability `P ≈ t^m/(γq)` with
  `γ ≥ m!`; total `m!·t·C/(γP) + Lin(t)`; with `t = q^e` the cost must satisfy
  `1/2 < e(m−1)` and `e ≤ 1/(2ω)` to be below `q^{1/2}`.
- §3 structure (PROVEN algebra): `J = ⟨F(x_1),…,F(x_m)⟩` has `#V(J) = d^m`
  rational zeros; Proposition 3: `#NS(Syz) = #V(J) − #V(I)`; degree bound
  `Reg = md + d_S − m` with `d_S = mδ` (eq. 13, Lemma 2); §5.2 interpolation
  formula for the cofactor `T` with leading monomial `x_1^{d−1}⋯x_m^{d−1}`.
- §4.1 lower bound: Lemma 6 (unnecessary signatures: monomials with all
  exponents `< d − δ`); Assumption 7 (semi-normality) and Remark 8
  (signature-based algorithms are the most efficient); Lemma 8: any efficient
  S-polynomial algorithm needs `≥ (d^m − (d−δ)^m)^{1−ε}` S-polynomials for
  almost every `a, b`, and `d^m − (d−δ)^m ≥ m·d^{m−1}` for `d > δ ≥ 4`;
  Proposition 9: `≥ (m·d^{m−1})^{1−ε}` field operations per Groebner basis.
  (HEURISTIC under Assumption 7 and Remark 8.)
- §4.1.3 consequence (eq. 17): total cost `≳ m!·m·q`, "more precisely ...
  greater than `q^{m(1−ε)/(m−1)}`. This implies that naive index calculus
  methods with Groebner basis computation by S-polynomials cannot be more
  efficient than Pollard's rho method. Moreover, based on our experimental
  observations, it cannot be more efficient than even the brute force method."
- §4.2: a second, algorithm-independent argument (Conjecture 10, Assumption
  11: the reduced cofactor support has size `≈ d^m`), confirmed on 53 of 60
  examples.
- §4.3 (EXPERIMENTAL, Risa/Asir, m = 3, 4, p of 10–25 bits): `#G* ≈ 2.1 ×
  m·d^{m−1}` for random-rooted `F`, for the binomial family `F = x^k − 1`
  (`k | p−1`, i.e. the multiplicative-subgroup base) and for `x^{k−1}+⋯+1`;
  "Lemma 8 and Assumption 11 seem to hold for all examples."
- §1 (as reported there): Kudo et al. 2018 "showed that both methods of
  [Amadori et al., Petit et al.] do not outperform generic algorithms such as
  the rho method".

## Relevance to this program

This is the published form of the CRT / `F_q^{d^m}` argument that
`H-ICEX-6ca21f` records as HEUR-ICEX-6ca21f-1 (that heuristic's floor `d^m`
is stronger than this paper's `m·δ·d^{m−1}`; both exceed the MITM enumeration
cost `d^{⌈m/2⌉}`). It bounds every Groebner-based decomposition over a split
base, including APS's known-log base (KN-LIT-1e6270) and PKM's subgroup base
(KN-LIT-9c442f). See `KR-IC-52ad34`, `KR-IC-dbf1b0`, `KR-IC-585a96`.

## Not verified here

The two statistical assumptions are the paper's; the experiments were not
reproduced.

## Provenance

Full text (Wayback copy of the De Gruyter open-access PDF) read on
2026-10-24 by a delegated literature lane of the session recorded in
DEC-20261025-48232f (`docs/reports/aps-prime-field-review-20261025/lanes/prime_field_barriers.md`).
