---
id: KN-LIT-ad6582
type: literature
title: "Mathematics of Public Key Cryptography (chapters 13, 15, 19 read): BSGS and interval DLP bounds, Semaev's prime-field factor base with 'no efficient algorithm even for n = 5; Coppersmith's method seems not to be useful', and the univariate/bivariate Coppersmith theorems"
authors:
  - "Steven D. Galbraith"
year: 2012
venue: "Cambridge University Press, 2012 (author's chapter PDFs online)"
identifiers:
  eprint: null
  arxiv: null
  doi: "10.1017/CBO9781139012843"
  url: "https://www.math.auckland.ac.nz/~sgal018/crypto-book/crypto-book.html"
tags: [textbook, ecdlp, index-calculus, prime-field, semaev, coppersmith, bsgs, interval-dlp]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

Textbook reference. The chapters read are the ones cited by the prime-field
summation-polynomial literature for the generic baselines and for the
explicit dismissal of lattice methods on Semaev's equation.

## Key claims (verified from the author's chapter PDFs)

- §15.8.1: factor base `B = {(x,y) ∈ E(F_p) : 0 ≤ x ≤ p^{1/n}}`,
  decomposition = solving `Summ_{n+1}(x_1,…,x_n, x_R) ≡ 0 (mod p)` with
  `0 ≤ x_i ≤ p^{1/n}` (eq. 15.12); "the expected number of points R that have
  to be selected before a relation is obtained is about n!"; "Unfortunately,
  no efficient algorithm is known for solving the polynomial equation (15.12)
  even for n = 5 (in which case the equation has degree 16 in each of its 5
  variables). Coppersmith's method (see Section 19.2) seems not to be useful
  for this task." Theorem 15.8.2: `Summ_n` is symmetric of degree `2^{n−2}`
  in each variable.
- §15.9.3: "By now, many people have tried and failed to discover an index
  calculus algorithm for the DLP on general elliptic curves. However, this
  does not prove that no such algorithm exists"; xedni's relation probability
  is "too low".
- Theorem 13.3.1: BSGS in a group of order r runs in `O(√r log^2 r)` bit
  operations with `O(√r log r)` bits of storage; Exercise 13.3.6: the DLP in
  an interval of length w in about `√(2w)` group operations with `√(w/2)`
  storage.
- Theorem 19.1.9 (univariate modular, PROVEN): roots `|x_0| < ½ M^{1/d−ε}`
  in time polynomial in `d, 1/ε, log M`; Theorem 19.2.1 (bivariate modular,
  total degree d, HEURISTIC): `XY < M^{1/d−ε}` yields two polynomials
  vanishing at the root, independence not guaranteed; Theorem 19.3.1
  (bivariate integer, degree d in each variable, PROVEN): `XY < W^{2/(3d)}`.

## Relevance to this program

The citable textbook statement that no solver exists for Semaev's bounded-root
equation and that Coppersmith's method is not expected to help; the generic
baselines (BSGS, interval DLP) every prime-field index-calculus row is
measured against. See `KR-IC-76aaed`.

## Not verified here

Other chapters.

## Provenance

Chapters 13, 15 and 19 read from the author's online PDFs on 2026-10-24 by a
delegated literature lane of the session recorded in DEC-20261025-48232f.
