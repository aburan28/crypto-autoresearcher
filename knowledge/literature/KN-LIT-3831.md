---
id: KN-LIT-3831
type: literature
title: "Faster Compact Diffie–Hellman: Endomorphisms on the x-line"
authors:
  - "Craig Costello"
  - "Huseyin Hisil"
  - "Benjamin Smith"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, endomorphism, glv-gls, implementation, pairing, protocol, provable-security, quantum, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe an implementation of fast elliptic curve scalar multiplication, optimized for Diffie–Hellman Key Exchange at the 128bit security level. The algorithms are compact (using only x-coordinates), run in constant time with uniform execution patterns, and do not distinguish between the curve and its quadratic twist; they thus have a built-in measure of side-channel resistance.

## Key claims (as reported)
- (For comparison, we also implement two faster but non-constant-time algorithms.) The core of our construction is a suite of two-dimensional differential addition chains driven by efficient endomorphism decompositions, built on curves selected from a family of Q-curve reductions over Fp2 with p = 2127 − 1.
- We include state-of-the-art experimental results for twist-secure, constant-time, x-coordinate-only scalar multiplication.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410275 (1).pdf`
- `downloads/84410275 (2).pdf`
- `downloads/84410275 (3).pdf`
- `downloads/84410275.pdf`
