---
id: KN-LIT-7214
type: literature
title: "Towards faster polynomial-time lattice reduction"
authors:
  - "Paul Kirchner"
  - "Thomas Espitau"
  - "Pierre-Alain Fouque"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, pairing, pqc, provable-security, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The lll algorithm is a polynomial-time algorithm for reducing d-dimensional lattice with exponential approximation factor. Currently, the most efficient variant of lll, by Neumaier and Stehlé, has a theoretical running time in d4 ·B 1+o(1) where B is the bitlength of the entries, but has never been implemented.

## Key claims (as reported)
- This work introduces new asymptotically fast, parallel, yet heuristic, reduction algorithms with their optimized implementations.
- Our algorithms are recursive and fully exploit fast matrix multiplication.
- We experimentally demonstrate that by carefully controlling the floating-point precision during the recursion steps, we can reduce euclidean lattices of rank d in time Õ(dω · C), i.e., almost a constant number of matrix multiplications, where ω is the exponent of matrix multiplication and C is the log of the condition number of the matrix.
- For cryptographic applications, C is close to B, while it can be up to d times larger in the worst case.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826302 (1).pdf`
- `downloads/12826302.pdf`
