---
id: KN-LIT-1651
type: literature
title: "Faster Polynomial Evaluations for SIMD FHEs and Application to BGV in HElib"
authors:
  - "Jiachen Zhao"
  - "Jiang Zhang( )"
  - "Binwu Xiang( )"
  - "Songyu Wu"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1089"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1089"
tags: [fhe, implementation, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The cost of homomorphic multiplications for existing FHEs to evaluate a degree-D polynomial f (x) at some point x is very expensive. When x is encoded in a plaintext slot having a power-of-two degree d = 2l and D ≤ d, one can efficiently evaluate f (x) with O(log d) multiplications using the heuristic algorithms of Okada et al.

## Key claims (as reported)
- However, neither d = 2l nor D ≤ d is satisfied for most practical√FHE parameters, and the Paterson–Stockmeyer (P-S) method with O( D) multiplications remains the state-of-the-art for d ̸= 2l or D > d.
- In this paper, we first present a polynomial evaluation algorithm with O(log d) multiplications for any non-power-of-two d and D ≤ d, which achieves the same asymptotic complexity as that ofpOkada et al.
- Then, we gave a polynomial evaluation algorithm with O( D/d) multiplications for plaintext modulus√p > 2 and d < D ≤ d log p, which beats the P-S method by a factor of d and essentially achieves logarithmic multiplication complexity when D ≤ d · min(log2 D, log p).
- As a major application, we implement our algorithms in experiment to evaluate the digit extraction polynomials of the BGV bootstrapping with parameter d ranging from 14 to 45 in HElib6 , and obtain a 1.22 − 2.16× speedup over the recent work of Ma et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1089.pdf`
