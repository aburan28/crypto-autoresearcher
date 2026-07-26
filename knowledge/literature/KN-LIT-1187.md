---
id: KN-LIT-1187
type: literature
title: "A COMPREHENSIVE ANALYSIS OF REGEV’S QUANTUM ALGORITHM"
authors:
  - "RAZVAN BARBULESCU"
  - "MUGUREL BARCAU"
  - "VICENŢIU PAŞOL"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1758"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1758"
tags: [dlp, elliptic-curve, factoring, index-calculus, number-theory, pairing, pollard-rho, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Public key cryptography can be based on integer factorization and the discrete logarithm problem (DLP), applicable in multiplicative groups and elliptic curves. Regev’s recent quantum algorithm was initially designed for the factorization and was later extended to the DLP in the multiplicative group.

## Key claims (as reported)
- In this article, we further extend the algorithm to address the DLP for elliptic curves.
- Notably, based on celebrated conjectures in Number Theory, Regev’s algorithm is asymptotically faster than Shor’s algorithm for elliptic curves.
- Our analysis covers all cases where Regev’s algorithm can be applied.
- We examine the general framework of Regev’s algorithm and offer a geometric description of its parameters.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1758.pdf`
