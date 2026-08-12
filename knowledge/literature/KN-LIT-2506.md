---
id: KN-LIT-2506
type: literature
title: "An Optimized Hardware Architecture for the Montgomery Multiplication Algorithm"
authors:
  - "Miaoqing Huang"
  - "Kris Gaj"
  - "Soonhak Kwon"
  - "Tarek El-Ghazawi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, implementation, pollard-rho, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Montgomery modular multiplication is one of the fundamental operations used in cryptographic algorithms, such as RSA and Elliptic Curve Cryptosystems. At CHES 1999, Tenca and Koç introduced a now-classical architecture for implementing Montgomery multiplication in hardware.

## Key claims (as reported)
- With parameters optimized for minimum latency, this architecture performs a single Montgomery multiplication in approximately 2n clock cycles, where n is the size of operands in bits.
- In this paper we propose and discuss an optimized hardware architecture performing the same operation in approximately n clock cycles with almost the same clock period.
- Our architecture is based on pre-computing partial results using two possible assumptions regarding the most significant bit of the previous word, and is only marginally more demanding in terms of the circuit area.
- The new radix-2 architecture can be extended for the case of radix-4, while preserving a factor of two speed-up over the corresponding radix-4 design by Tenca, Todorov, and Koç from CHES 2001.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49390215 (1).pdf`
- `downloads/49390215 (2).pdf`
- `downloads/49390215 (3).pdf`
- `downloads/49390215.pdf`
