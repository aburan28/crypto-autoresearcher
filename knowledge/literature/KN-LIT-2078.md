---
id: KN-LIT-2078
type: literature
title: "A heuristic quasi-polynomial algorithm for discrete logarithm in finite fields of small characteristic"
authors:
  - "Razvan Barbulescu"
  - "Pierrick Gaudry"
  - "Antoine Joux"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, finite-field, groebner, number-theory, pairing, prime-field]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The difficulty of computing discrete logarithms in fields Fqk depends on the relative sizes of k and q. Until recently all the cases had a sub-exponential complexity of type L(1/3), similar to the factorization problem.

## Key claims (as reported)
- In 2013, Joux designed a new algorithm with a complexity of L(1/4 + ) in small characteristic.
- In the same spirit, we propose in this article another heuristic algorithm that provides a quasi-polynomial complexity when q is of size at most comparable with k.
- By quasi-polynomial, we mean a runtime of nO(log n) where n is the bit-size of the input.
- For larger values of q that stay below the limit Lqk (1/3), our algorithm loses its quasi-polynomial nature, but still surpasses the Function Field Sieve.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410132 (1).pdf`
- `downloads/84410132 (2).pdf`
- `downloads/84410132 (3).pdf`
- `downloads/84410132.pdf`
