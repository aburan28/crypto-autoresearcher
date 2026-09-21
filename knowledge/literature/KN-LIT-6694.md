---
id: KN-LIT-6694
type: literature
title: "Single Base Modular Multiplication for Efficient Hardware RNS Implementations of ECC"
authors:
  - "Karim Bigou"
  - "Arnaud Tisserand"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, implementation, lattice, pairing, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The paper describes a new RNS modular multiplication algorithm for efficient implementations of ECC over FP . Thanks to the proposition of RNS-friendly Mersenne-like primes, the proposed RNS algorithm requires 2 times less moduli than the state-of-art ones, leading to 4 times less precomputations and about 2 times less operations.

## Key claims (as reported)
- FPGA implementations of our algorithm are presented, with area reduced up to 46 %, for a time overhead less than 10 %.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930121 (1).pdf`
- `downloads/92930121.pdf`
