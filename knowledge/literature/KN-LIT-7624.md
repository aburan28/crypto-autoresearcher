---
id: KN-LIT-7624
type: literature
title: Endomorphisms of abelian varieties over finite fields
authors: [Tate John]
year: 1966
venue: Inventiones mathematicae, 2:134-144
identifiers:
  eprint: null
  doi: 10.1007/BF01404549
  url: https://link.springer.com/article/10.1007/BF01404549
tags: [abelian-variety, endomorphism, tate-module, isogeny, finite-field, honda-tate, foundational, number-theory, algebraic-geometry]
confidence: reported
citation_verified: web
added: 2026-07-31
superseded_by: null
---

## Contribution
Proves that over a finite field k, the natural map
Z_ℓ ⊗ Hom_k(A', A'') → Hom_G(T_ℓ(A'), T_ℓ(A'')) is bijective for ℓ ≠ char(k).
Consequently, abelian varieties over finite fields are determined up to
isogeny by the Galois action on their Tate modules / Frobenius
characteristic polynomials.

## Key claims (as reported)
- Main theorem: the Hom–Tate-module map is an isomorphism when k is finite.
- Immediate corollary used everywhere later: two abelian varieties over F_q
  are isogenous iff their Frobenius characteristic polynomials coincide.
- Supplies the *injective* half of the Honda–Tate classification (surjectivity
  is Honda 1968, KN-LIT-7625).

## Relevance to this program
Foundational for every finite-field isogeny / endomorphism-ring argument in
the corpus (KN-TECH-028, KN-TECH-024–029, Waterhouse KN-LIT-7626). Any
proposal that treats “Frobenius characteristic polynomial determines the
isogeny class” as a new observation is `known`. Does not by itself give an
ECDLP algorithm.

## Not verified here
Full proof not re-derived. Bibliographic identity confirmed against the
Inventiones / EDML record (vol. 2, pp. 134–144, 1966) and DOI
10.1007/BF01404549. The axiomatized Hyp(k,A,d,ℓ) framework inside the paper
was not checked beyond the main-theorem statement.
