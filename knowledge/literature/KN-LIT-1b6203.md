---
id: KN-LIT-1b6203
type: literature
title: "Factoring into coprimes in essentially linear time"
authors:
  - "Daniel J. Bernstein"
year: 2004
venue: "preprint (author's page)"
identifiers:
  doi: null
  arxiv: null
  url: "https://cr.yp.to/papers.html#dcba"
tags: [factorization, standalone, integer, number-theory, bernstein, complexity]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
For a finite set S of positive integers, computes the natural coprime base for
S (each element of S a product of powers of elements of the base) in
essentially linear time, and factors S into elements of that base at the same
cost. Best previous result was a quadratic-time algorithm of Bach–Driscoll–
Shallit. The algorithms use only small constant auxiliary space per element.

## Key claims (as reported)
- Coprime-base computation and the in-base factorization run in essentially
  linear time (almost linear in the combined bit length of S).
- Improves the quadratic-time previous algorithm of Bach, Driscoll, and
  Shallit.
- The paper states the algorithms are "essentially linear time", i.e. linear
  up to negligible lower-order polylogarithmic factors; not exact linear time.

## Relevance
- Classic algorithmic number theory relevant to sieving/pre-factorization
  stages in NFS-style and index-calculus contexts; useful for the program
  when describing preprocessing of factor bases. Single-result paper; not an
  ECDLP advance.

## Not verified here
- Full proof of the linear-time bound not re-derived; recorded from the paper
  abstract and structure.