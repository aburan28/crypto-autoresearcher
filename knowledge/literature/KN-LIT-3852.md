---
id: KN-LIT-3852
type: literature
title: "FASTER SQUARE ROOTS IN ANNOYING FINITE FIELDS"
authors:
  - "DANIEL J. BERNSTEIN"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, finite-field, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let q be an odd prime number. There are several methods known to compute square roots in Z/q: the quadratic-extension methods of Legendre, Pocklington, Cipolla, Lehmer, et al., and the discrete-logarithm methods of Tonelli, Shanks, et al.

## Key claims (as reported)
- The quadratic-extension methods use (3 + o(1)) lg q multiplications and, on average, 2 + o(1) Jacobi-symbol computations mod q.
- The discrete-logarithm methods use only (1 + o(1)) lg q multiplications, √ after an easy precomputation of one element of Z/q, if ord2 (q − 1) ∈ o( lg q).
- This paper presents an algorithm that uses only (1 + o(1)) lg q multiplications, O(1) elements of Z/q, if ord (q − 1) ∈ after 2 √ an easy precomputation of (lg q) o( lg q lg lg q).
- For example, the new algorithm can compute square roots in Z/q for q = 2224 − 296 + 1 using 364 multiplications in Z/q and 1024 precomputed elements of Z/q.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/sqroot-20011123-retypeset20220327.pdf`
