---
id: KN-LIT-3833
type: literature
title: "Faster ECC over F2521 −1"
authors:
  - "Robert Granger"
  - "Michael Scott"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, implementation, prime-field, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present a new multiplication algorithm for residues modulo the Mersenne prime 2521 − 1. Using this approach, on an Intel Haswell Core i7-4770, constant-time variable-base scalar multiplication on NIST’s (and SECG’s) curve P-521 requires 1,108,000 cycles, while on the recently proposed Edwards curve E-521 it requires just 943,000 cycles.

## Key claims (as reported)
- As a comparison, on the same architecture openSSL’s ECDH speed test for curve P-521 requires 1,319,000 cycles.
- Furthermore, our code was written entirely in C and so is robust across different platforms.
- The basic observation behind these speedups is that the form of the modulus allows one to multiply residues with as few word-by-word multiplications as is needed for squaring, while incurring very little overhead from extra additions, in contrast to the usual Karatsuba methods.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200185 (1).pdf`
- `downloads/90200185 (2).pdf`
- `downloads/90200185 (3).pdf`
- `downloads/90200185 (4).pdf`
- `downloads/90200185.pdf`
