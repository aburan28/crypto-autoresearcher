---
id: KN-LIT-287
type: literature
title: "Fast Exhaustive Search for Polynomial Systems in F2"
authors:
  - "Tung Chou"
  - "Ruben Niederhagen"
  - "Adi Shamir"
  - "Bo-Yin Yang"
year: 2010
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2010/313"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2010/313"
tags: [cryptanalysis, groebner, hash, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We analyze how fast we can solve general systems of multivariate equations of various low degrees over F2 ; this is a well known hard problem which is important both in itself and as part of many types of algebraic cryptanalysis. Compared to the standard exhaustive search technique, our improved approach is more efficient both asymptotically and practically.

## Key claims (as reported)
- We implemented several optimized versions of our techniques on CPUs and GPUs.
- Our technique runs more than 10 times faster on modern graphic cards than on the most powerful CPU available.
- Today, we can solve 48+ quadratic equations in 48 binary variables on a 500-dollar NVIDIA GTX 295 graphics card in 21 minutes.
- With this level of performance, solving systems of equations supposed to ensure a security level of 64 bits turns out to be feasible in practice with a modest budget.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62250195 (1).pdf`
- `downloads/62250195 (2).pdf`
- `downloads/62250195 (3).pdf`
- `downloads/62250195.pdf`
