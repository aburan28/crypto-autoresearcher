---
id: KN-LIT-9c442f
type: literature
title: "Algebraic approaches for the elliptic curve discrete logarithm problem over prime fields (full text read): compositional factor bases, the smooth-order multiplicative-subgroup and isogeny-kernel-coset bases, and the p^{1/2-1/m} per-system threshold"
authors:
  - "Christophe Petit"
  - "Michiel Kosters"
  - "Ange Messeng"
year: 2016
venue: "PKC 2016, LNCS 9614, pp. 3-18"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1007/978-3-662-49387-8_1"
  url: "https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf"
tags: [index-calculus, prime-field, point-decomposition, groebner, factor-base, multiplicative-subgroup, isogeny-kernel, ecdlp]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

Generalises the binary-curve decomposition systems to `E(F_p)` by taking the
factor base `F = {(x,y) ∈ E(K) : L(x) = 0}` for a high-degree rational map `L`
that is a composition of low-degree maps `L_j`, so that `L(x) = 0` becomes a
chain of low-degree equations. Two concrete bases are given, a cost formula
is derived, and the authors conclude the attacks are not practical and their
asymptotic complexity unknown. Supersedes the abstract-only stub KN-LIT-025.

## Key claims (verified from the full text)

- §1: "Diem and Gaudry's attacks implicitly use `L(x) = x^q − x` where q is
  the size of a subfield; ... Semaev's original factor basis implicitly uses
  `L(x) = ∏_{α<B}(x − α)`." Conditions on `L` (§3.1): `|{x ∈ F_p : L(x) = 0}|
  ≈ |{x ∈ \bar F_p : L(x) = 0}| ≈ p^{1/m}` and `L` a composition of low-degree
  maps. System (4): `S_{m+1}(x_{11},…,x_{m1},X) = 0`, `x_{i,j+1} = L_j(x_{i,j})`,
  `L_{n'}(x_{i,n'}) = 0`.
- §3.2 (HEURISTIC): expected solutions `(deg L)^m/(m!·p)`; total cost
  `P(p,m) + (m!·p/(deg L)^{m−1})·T(E,m,L) + (deg L)^ω`; "Our algorithm will
  outperform generic discrete logarithm algorithms when this complexity is
  smaller than `p^{1/2}`. When `(deg L)^m ≈ m!·p`, this will happen when one
  can solve `T(E,m,L)` more efficiently than `p^{1/2−1/m}`."
- §3.3 (multiplicative subgroup): "assume that `p − 1 = r ∏ p_i` ... We define
  V as the subgroup G of order `∏ p_i` in `F_p^*`. We then set `L_j(x) =
  x^{p_j}` ... Alternatively, we could also choose V as a coset aG of G."
  NIST P-224's `p − 1` is noted as smooth enough "for m ≥ 3 and B = 2".
- §3.4 (arbitrary p): auxiliary curve `E'/F_p` of smooth order, `V` = the
  x-coordinates of a coset of a smooth-order subgroup `H`, `L` built from Vélu
  isogenies; Lemma 1: `|{x : L(x) = 0}| = ∏ p_i` (PROVEN).
- §3.5: precomputation (curve search ≈ `p^{1/m}` trials for B = 2; Table 1
  gives `2^54` / `2^86` for |p| = 160 / 256 at m = 3); a chosen-p "back door"
  variant is judged unlikely to matter.
- §4 (EXPERIMENTAL, Magma V2.18-5, m = 2 only): Table 4 (p − 1 subgroups):
  n_1 = 11, p = 4 206 593, degree of regularity 6, 4 975 s, 2 266 MB;
  Table 5 (isogeny kernel): p = 3 173 683, 5 163 s. "The degrees of
  regularity, time and memory requirements seem to increase a bit faster in
  the prime case than in the binary case."
- §5: "The attacks are not practical at the moment and we do not know their
  asymptotic complexity." Problem 1 (generalized root-finding): find
  `X_i ∈ K` with `f(X_1,…,X_m) = 0` and `L(X_i) = 0`; a dedicated non-Groebner
  algorithm is called "an even more important problem". The committee-suggested
  control, Groebner bases on Semaev's interval system `L(x) = ∏_{α<B}(x − α)`,
  was "intriguingly ... easier to solve than ours", which "may either suggest
  that our approach is unlikely to be efficient asymptotically, or that
  Semaev's original attack should be revisited from an algebraic perspective."

## Relevance to this program

The multiplicative-subgroup and coset bases are this paper's §3.3, so they
are prior art, not a new lead. The observation that the chained (low-degree)
presentation was no easier than the split polynomial is what the CRT /
0-dimensional-variety argument predicts (`KR-IC-585a96`): the constraint
algebra is `F_p^{|V|^m}` whichever way it is written. The per-system threshold
`T < p^{1/2−1/m}` is the citable form of "what an oracle must achieve".

## Not verified here

Nothing beyond the paper's own hedges; its experiments were not reproduced.

## Provenance

Full text (author's PDF) read on 2026-10-24 by two delegated literature lanes
of the session recorded in DEC-20261025-48232f (notes under
`docs/reports/aps-prime-field-review-20261025/lanes/`).
