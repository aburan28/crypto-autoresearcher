---
id: KN-LIT-1134
type: literature
title: "New Space-Efficient Quantum Algorithm for Binary Elliptic Curves using the Optimized Division Algorithm"
authors:
  - "Hyeonhak Kim"
  - "Seokhie Hong"
year: 2023
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2303.06570"
  url: "https://arxiv.org/abs/2303.06570"
tags: [cryptanalysis, dlp, ecdlp, elliptic-curve, finite-field, implementation, protocol, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In previous research, quantum resources were concretely estimated for solving Elliptic Curve Discrete Logarithm Problem(ECDLP). In [BBVHL20], the quantum algorithm was optimized for the binary elliptic curves and the main optimization target was the number of the logical qubits.

## Key claims (as reported)
- The division algorithm was mainly optimized in [BBVHL20] since every ancillary qubit is used in the division algorithm.
- In this paper, we suggest a new quantum division algorithm on the binary field which uses a smaller number of qubits.
- For elements in a field of 2n , we can save ⌈n/2⌉ − 1 qubits instead of using 8n2 + 4n − 12 + (16n − 8)⌊log(n)⌋ more Toffoli gates, which leads to a more space-efficient quantum algorithm for binary elliptic curves.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2303.06570v1 (1).pdf`
- `downloads/2303.06570v1.pdf`
