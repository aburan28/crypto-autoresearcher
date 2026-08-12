---
id: KN-LIT-1333
type: literature
title: "A note on “a fully dynamic multi-secret sharing scheme with redundant authorization”"
authors:
  - "Zhengjun Cao"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2329"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2329"
tags: [dlp, ecdlp, elliptic-curve, finite-field, hash, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the secret sharing scheme [Cryptogr. 16(1): 3-20 (2024)] cannot be put into practice.

## Key claims (as reported)
- (1) It confused the elements in a residue class ring modulo a prime p with the points in an elliptic curve group over the finite field Fp .
- (2) It confused the underlying elliptic curve with the Lagrange interpolating curve, and falsely requires the interpolating polynomial to map a point on the elliptic curve to another point on the same elliptic curve.
- (3) It misuses the bit-wise XOR operator for the operands with unequal bit-length, which results in the exposure of any participant’s share, and the loss of confidentiality.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2329.pdf`
