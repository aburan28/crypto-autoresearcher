---
id: KN-LIT-036
type: literature
title: An introduction to commutative and noncommutative Grobner bases
authors: [Mora Teo]
year: 1994
venue: Theoretical Computer Science, 134(1):131-173
identifiers:
  eprint: null
  doi: 10.1016/0304-3975(94)90283-6
  url: https://www.sciencedirect.com/science/article/pii/0304397594902836
tags: [noncommutative, groebner, free-algebra, word-problem, path-algebra, quiver, semi-decidable]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Presents Grobner bases uniformly as a finite model of a (generally infinite)
linear Gauss-reduced basis of an ideal, with Buchberger's algorithm as the
generalization of Gaussian elimination, and extends the theory from the
commutative polynomial ring to the *free associative algebra* and other
noncommutative algebras.

## Key claims (as reported)
- Links noncommutative Grobner bases to the word problem; stresses that they may
  be INFINITE, so only a partial (semi-decidable, non-terminating in general)
  procedure exists.
- Foundational NC completion machinery: Mora, "Grobner bases for non-commutative
  polynomial rings," AAECC-3, LNCS 229:353-362, 1986 (doi:10.1007/3-540-16776-5_740).
  Path-algebra specialization: Green, "Noncommutative Grobner bases, and
  projective resolutions," Progress in Math. 173:29-60, 1999
  (doi:10.1007/978-3-0348-8716-8_2). Two-sided quiver algorithm: Waweru-Maingi,
  arXiv:2306.06457 (2023).

## Relevance to this program
Frames free-algebra (word-level) Grobner computation and its link to the word
problem, grounding the program's noncommutative path-algebra candidate
(RQ-NCP-001, KN-TECH-014, KN-OPEN-008): model translations/negation/correspondences
as quiver arrows and search for word-level relations the commutative subset-sum
quotient misses. The semi-decidability is the core risk: unbounded overlap
reduction has no birthday-style bound, and the commutator-collapse argument may
show word relations shadow commutative ones.

## Not verified here
Full paper not read; the free-algebra Grobner framing and semi-decidability are
textbook-level (hence confidence: established). Fields (incl. the 1986 Mora,
Green, Waweru-Maingi) confirmed against Elsevier/Springer/arXiv records via
search, not by fetching the primary pages.
