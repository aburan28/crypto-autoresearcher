---
id: KN-LIT-2100
type: literature
title: "A Low-Cost ECC Coprocessor for Smartcards"
authors:
  - "Harald Aigner"
  - "Holger Bock"
  - "Markus Hütter"
  - "Johannes Wolkerstorfer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, elliptic-curve, finite-field, implementation, pairing, prime-field, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article we present a low-cost coprocessor for smartcards which supports all necessary mathematical operations for a fast calculation of the Elliptic Curve Digital Signature Algorithm (ECDSA) based on the finite field GF(2m ). These ECDSA operations are GF(2m ) addition, 4-bit digit-serial multiplication in GF(2m ), inversion in GF(2m ), and inversion in GF(p).

## Key claims (as reported)
- An efficient implementation of the multiplicative inversion which breaks the 11:1 limit regarding multiplications makes it possible to use affine instead of projective coordinates for point operations on elliptic curves.
- A bitslice architecture allows an easy adaptation for different bit lengths.
- A small chip area is achieved by reusing the hardware registers for different operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560104 (1).pdf`
- `downloads/31560104 (2).pdf`
- `downloads/31560104.pdf`
