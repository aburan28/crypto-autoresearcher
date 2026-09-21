---
id: KN-LIT-3780
type: literature
title: "Families of SNARK-friendly 2-chains of elliptic curves"
authors:
  - "Youssef El Housni"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, implementation, lattice, pairing, prime-field, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CANS’20, El Housni and Guillevic introduced a new 2-chain of pairing-friendly elliptic curves for recursive zero-knowledge Succinct Non-interactive ARguments of Knowledge (zk-SNARKs) made of the former BLS12-377 curve (a Barreto–Lynn–Scott curve over a 377bit prime field) and the new BW6-761 curve (a Brezing–Weng curve of embedding degree 6 over a 761-bit prime field). First we generalise the curve construction, the pairing formulas (e : G1 × G2 → GT ) and the group operations to any BW6 curve defined on top of any BLS12 curve, forming a family of 2-chain pairing-friendly curves.

## Key claims (as reported)
- Second, we investigate other possible 2-chain families made on top of the BLS12 and BLS24 curves.
- We compare BW6 to Cocks–Pinch curves of higher embedding degrees 8 and 12 (CP8, CP12) at the 128-bit security level.
- We derive formulas for efficient optimal ate and optimal Tate pairings on our new CP curves.
- We show that for both BLS12 and BLS24, the BW6 construction always gives the fastest pairing and curve arithmetic compared to Cocks-Pinch curves.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760128 (1).pdf`
- `downloads/132760128.pdf`
