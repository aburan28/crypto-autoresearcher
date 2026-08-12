---
id: KN-LIT-3808
type: literature
title: "Fast Multi-Precision Multiplication for Public-Key Cryptography on Embedded Microprocessors"
authors:
  - "Michael Hutter"
  - "Erich Wenger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, prime-field, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-precision multiplication is one of the most fundamental operations on microprocessors to allow public-key cryptography such as RSA and Elliptic Curve Cryptography (ECC). In this paper, we present a novel multiplication technique that increases the performance of multiplication by sophisticated caching of operands.

## Key claims (as reported)
- Our method significantly reduces the number of needed load instructions which is usually one of the most expensive operation on modern processors.
- We evaluate our new technique on an 8-bit ATmega128 microcontroller and compare the result with existing solutions.
- Our implementation needs only 2, 395 clock cycles for a 160-bit multiplication which outperforms related work by a factor of 10 % to 23 %.
- The number of required load instructions is reduced from 167 (needed for the best known hybrid multiplication) to only 80.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170459 (1).pdf`
- `downloads/69170459 (2).pdf`
- `downloads/69170459 (3).pdf`
- `downloads/69170459.pdf`
