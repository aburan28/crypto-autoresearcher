---
id: KN-LIT-be0bfd
type: literature
title: "The Matrix Reloaded: Multiplication Strategies in FrodoKEM"
authors:
  - "Joppe W. Bos"
  - "Maximilian Ofner"
  - "Joost Renes"
  - "Tobias Schneider"
  - "Christine van Vredendaal"
year: 2021
venue: "Proceedings of the 20th International Conference on Cryptology and Network Security (CANS 2021)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [pqc, lattices, frodokem, implementation, matrix, avx2]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Analyses and optimises the multiplication strategies for the FrodoKEM
lattice-based key encapsulation mechanism: splitting the Frodo sample matrix
multiplication into independent "tile" multiplications, vectorised with SIMD
(SSE/AVX2) instructions, and comparing strategies (matrix products per row).
Provides a synchronised review of matrix product implementations with the
goal to speed up the FrodoKEM multiplication (the main cost) on x86 platforms.

## Key claims (as reported)
- Different multiplication strategies are compared and combined; the fastest
  implementation multiplies Frodo-640 matrix A·S with vectorised instructions,
  achieving a notable speedup over the reference implementation.
- Verifiable cost estimates used to argue constant-time implementation
  (no secret-dependent branches or memory access).

## Relevance
- Peripheral to ECDLP but a reference for constant-time/lattice cost of the
  "matrix multiplication" family of computations; potentially useful as a
  comparison of micro-optimised multiplication strategies in parallel
  hardware for side-stacks.
- Not an ECDLP claim.

## Not verified here
- Speedup numbers and the arm architecture benchmarks were not re-run; relayed
  from the paper.