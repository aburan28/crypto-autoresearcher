---
id: KN-LIT-037
type: literature
title: Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities
authors: [Coppersmith Don]
year: 1997
venue: Journal of Cryptology, 10(4):233-260
identifiers:
  eprint: null
  doi: 10.1007/s001459900030
  url: https://link.springer.com/article/10.1007/s001459900030
tags: [coppersmith, small-roots, lattice, lll, howgrave-graham, windowed, summation-polynomial]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
An LLL-based lattice method for finding *small* roots: integer roots of a
univariate polynomial modulo N (recovered up to ~N^{1/d} for degree d), and
small roots of a bivariate polynomial over the integers, with partial extension
to more variables. The foundational "Coppersmith method."

## Key claims (as reported)
- Univariate mod-N roots up to N^{1/d}; applications include low-exponent RSA and
  factoring N given a fraction of the bits of a factor.
- Practical reformulation: Howgrave-Graham, "Finding small roots of univariate
  modular equations revisited," IMA C&C 1997, LNCS 1355:131-142
  (doi:10.1007/BFb0024458) -- the Howgrave-Graham lemma: a low-norm polynomial
  with a small modular root has that root exactly over Z, reducing small-root
  finding to short-vector extraction (LLL).

## Relevance to this program
The machinery behind the program's windowed relation-finding candidate (round-2
B3, EXP-COPP-001): apply a Howgrave-Graham shift lattice to the bivariate Semaev
polynomial S_3(x_1,x_2) restricted to a window [0,X]x[0,Y], recovering a
*certified complete* list of relations inside the window. Its value depends on
whether relation x-coordinates concentrate in a window -- which tensions against
the equidistribution / quasirandomness expectation (KN-TECH-016); if relations
equidistribute, windowing buys nothing and lattice overhead loses.

## Not verified here
Full paper not read; the small-root method and the Howgrave-Graham lemma are
textbook-level in lattice cryptanalysis (hence confidence: established). Fields
confirmed against the J. Cryptology / Springer DOI records via search, not by
fetching the primary pages (issue number 4 search-inferred).
