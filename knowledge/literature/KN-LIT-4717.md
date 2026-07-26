---
id: KN-LIT-4717
type: literature
title: "Lifting and Elliptic Curve Discrete Logarithms"
authors:
  - "Joseph H. Silverman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, ecdlp, elliptic-curve, index-calculus, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The difficulty of the elliptic curve discrete logarithm problem (ECDLP) underlies the attractiveness of elliptic curves for use in cryptography. The index calculus is a lifting algorithm that solves the classical finite field discrete logarithm problem in subexponential time, but no such algorithm is known in general for elliptic curves.

## Key claims (as reported)
- It turns out that there are four distinct lifting scenarios that one can use in attempting to solve the ECDLP; the lifting field may be a local field or a global field, and the lifted points may be torsion points or nontorsion points.
- These choices lead to four quite different ways to try to solve the ECDLP via lifting.
- None of these approaches has led to a solution to the ECDLP, but each method has its own reasons for failing to work.
- In this article I survey the four ways of lifting the ECDLP, explain their similarities and their differences, and describe the distinct roadblocks that arise in each case.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/978-3-642-04159-4_6.pdf`
