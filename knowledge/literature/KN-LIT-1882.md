---
id: KN-LIT-1882
type: literature
title: "Space-Efficient Quantum Algorithm for Elliptic Curve Discrete Logarithms with Resource Estimation"
authors:
  - "Han Luo∗"
  - "Ziyi Yang∗"
  - "Ziruo Wang"
  - "Yuexin Su"
  - "Tongyang Li"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2604.02311"
  url: "https://arxiv.org/abs/2604.02311"
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, factoring, finite-field, pairing, pollard-rho, prime-field, protocol, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Solving the Elliptic Curve Discrete Logarithm Problem (ECDLP) is critical for evaluating the quantum security of widely deployed elliptic-curve cryptosystems. Consequently, minimizing the number of logical qubits required to execute this algorithm is a key object.

## Key claims (as reported)
- In implementations of Shor’s algorithm, the space complexity is largely dictated by the modular inversion operation during point addition.
- Starting from the extended Euclidean algorithm (EEA), we refine the register-sharing method of Proos and Zalka and propose a space-efficient reversible modular inversion algorithm.
- We use length registers together with location-controlled arithmetic to store the intermediate variables in a compact form throughout the computation.
- We then optimize the stepwise update rules and give concrete circuit constructions for the resulting controlled arithmetic components.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2604.02311v2 (1).pdf`
- `downloads/2604.02311v2 (2).pdf`
- `downloads/2604.02311v2.pdf`
