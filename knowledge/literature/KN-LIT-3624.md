---
id: KN-LIT-3624
type: literature
title: "Efficient Ring-LWE Encryption on 8-bit"
authors:
  - "Howon Kim"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, implementation, lattice, mov-fr, pqc, protocol, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Public-key cryptography based on the “ring-variant” of the Learning with Errors (ring-LWE) problem is both efficient and believed to remain secure in a post-quantum world. In this paper, we introduce a carefully-optimized implementation of a ring-LWE encryption scheme for 8-bit AVR processors like the ATxmega128.

## Key claims (as reported)
- Our research contributions include several optimizations for the Number Theoretic Transform (NTT) used for polynomial multiplication.
- More concretely, we describe the Move-and-Add (MA) and the Shift-Add-Multiply-Subtract-Subtract (SAMS2) technique to speed up the performance-critical multiplication and modular reduction of coefficients, respectively.
- We take advantage of incompletely-reduced intermediate results to minimize the total number of reduction operations and use a special coefficient-storage method to decrease the RAM footprint of NTT multiplications.
- In addition, we propose a byte-wise scanning strategy to improve the performance of a discrete Gaussian sampler based on the Knuth-Yao random walk algorithm.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930640 (1).pdf`
- `downloads/92930640.pdf`
