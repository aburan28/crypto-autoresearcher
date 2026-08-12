---
id: KN-LIT-709
type: literature
title: "Speeding Up Elliptic Curve Multiplication with Mixed-base Representation for Applications to SIDH Ciphers"
authors:
  - "Wesam Eid"
  - "Marius Silaghi"
year: 2019
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1905.06492"
  url: "https://arxiv.org/abs/1905.06492"
tags: [curve-arithmetic, elliptic-curve, isogeny, pqc, protocol, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Elliptic curve multiplications can be improved by replacing the standard ladder algorithm’s base 2 representation of the scalar multiplicand, with mixed-base representations with power-of-2 bases, processing the n bits of the current digit in one optimized step. For this purpose, we also present a new methodology to compute, for Weierstrass form elliptic curves in the affine plane, operations of the type mP + nQ where m and n are small integers.

## Key claims (as reported)
- This provides implementations with the lower cost than previous algorithms, using only one inversion.
- In particular, the proposed techniques enable more opportunities for optimizing computations, leading to an important speed-up for applications based on elliptic curves, including the post-quantum cryptosystem Super Singular Isogeny Diffie Hellman (SIDH).

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1905.06492v2.pdf`
