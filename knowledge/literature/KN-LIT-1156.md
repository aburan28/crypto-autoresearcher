---
id: KN-LIT-1156
type: literature
title: "Quantum Circuit Designs of Point Doubling Operation for Binary Elliptic Curves"
authors:
  - "Harashta Tatimma Larasati"
  - "Howon Kim"
year: 2023
venue: "arXiv preprint"
identifiers:
  eprint: "iacr:2023/1140"
  doi: null
  arxiv: "2306.07530"
  url: "https://arxiv.org/abs/2306.07530"
tags: [cryptanalysis, curve-arithmetic, dlp, ecdlp, elliptic-curve, pairing, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the past years, research on Shor’s algorithm for solving elliptic curves for discrete logarithm problems (Shor’s ECDLP), the basis for cracking elliptic curve-based cryptosystems (ECC), has started to garner more significant interest. To achieve this, most works focus on quantum point addition subroutines to realize the double scalar multiplication circuit, an essential part of Shor’s ECDLP, whereas the point doubling subroutines are often overlooked.

## Key claims (as reported)
- In this paper, we investigate the quantum point doubling circuit for the stricter assumption of Shor’s algorithm when doubling a point should also be taken into consideration.
- In particular, we analyze the challenges on implementing the circuit and provide the solution.
- Subsequently, we design and optimize the corresponding quantum circuit, and analyze the high-level quantum resource cost of the circuit.
- Additionally, we discuss the implications of our findings, including the concerns for its integration with point addition for a complete double scalar multiplication circuit and the potential opportunities resulting from its implementation.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1140 (1).pdf`
- `downloads/2023-1140 (2).pdf`
- `downloads/2023-1140.pdf`
- `downloads/2306.07530v1.pdf`
