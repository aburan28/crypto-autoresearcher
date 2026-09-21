---
id: KN-LIT-574
type: literature
title: "Super-Isolated Elliptic Curves and Abelian Surfaces in Cryptography"
authors:
  - "Travis Scholl"
year: 2017
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1705.02316"
  url: "https://arxiv.org/abs/1705.02316"
tags: [abelian-variety, complexity-theory, ecdlp, elliptic-curve, extension-field, finite-field, isogeny, pairing, pollard-rho, prime-field, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We call a simple abelian variety over Fp super-isolated if its (Fp -rational) isogeny class contains no other varieties. The motivation for considering these varieties comes from concerns about isogeny based attacks on the discrete log problem.

## Key claims (as reported)
- We heuristically estimate that √ the number of super-isolated elliptic curves over Fp with prime order and p ≤ N , is roughly Θ̃( N ).
- In contrast, we prove that there are only 2 super-isolated surfaces of cryptographic size and nearprime order.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1705.02316v1 (1).pdf`
- `downloads/1705.02316v1 (2).pdf`
- `downloads/1705.02316v1.pdf`
