---
id: KN-LIT-4282
type: literature
title: "HOW TO FIND SMOOTH PARTS OF INTEGERS"
authors:
  - "DANIEL J. BERNSTEIN"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, pollard-rho]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let P be a finite set of primes, and let S be a finite sequence of positive integers. This paper presents an algorithm to find the largest P smooth divisor of each integer in S.

## Key claims (as reported)
- The algorithm takes time b(lg b)2+o(1) , where b is the total number of bits in P and S.
- A previous algorithm by the author takes time b(lg b)3+o(1) to find all the factors from P of each integer in S; a variant by Franke, Kleinjung, Morain, and Wirth usually takes time b(lg b)2+o(1) to find the largest P -smooth divisor of each integer in S; the algorithm in this paper always takes time b(lg b)2+o(1) to find the largest P smooth divisor of each integer in S.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/smoothparts-20040510.pdf`
