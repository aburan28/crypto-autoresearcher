---
id: KN-LIT-2498
type: literature
title: "An Improved RNS Variant of the BFV Homomorphic Encryption Scheme"
authors:
  - "Shai Halevi"
  - "Yuriy Polyakov"
  - "Victor Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an optimized implementation of the Fan-Vercauteren variant of Brakerski’s scale-invariant homomorphic encryption scheme. Our algorithmic improvements focus on optimizing decryption and homomorphic multiplication in the Residue Number System (RNS), using the Chinese Remainder Theorem (CRT) to represent and manipulate the large coefficients in the ciphertext polynomials.

## Key claims (as reported)
- In particular, we propose efficient procedures for scaling and CRT basis extension that do not require translating the numbers to standard (positional) representation.
- Compared to the previously proposed RNS design due to Bajard et al.
- [3], our procedures are simpler and faster, and introduce a lower amount of noise.
- We implement our optimizations in the PALISADE library and evaluate the runtime performance for the range of multiplicative depths from 1 to 100.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/rns-bfv.pdf`
