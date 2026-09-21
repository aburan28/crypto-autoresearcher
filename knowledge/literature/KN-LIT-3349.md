---
id: KN-LIT-3349
type: literature
title: "Curve41417: Karatsuba revisited"
authors:
  - "Daniel J. Bernstein"
  - "Chitchanok Chuengsatiansup"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, hyperelliptic, implementation, prime-field, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces constant-time ARM Cortex-A8 ECDH software that (1) is faster than the fastest ECDH option in the latest version of OpenSSL but (2) achieves a security level above 2200 using a prime above 2400 . For comparison, this OpenSSL ECDH option is not constant-time and has a security level of only 280 .

## Key claims (as reported)
- The new speeds are achieved in a quite different way from typical prime-field ECC software: they rely on a synergy between Karatsuba’s method and choices of radix smaller than the CPU word size.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310226 (1).pdf`
- `downloads/87310226 (2).pdf`
- `downloads/87310226 (3).pdf`
- `downloads/87310226.pdf`
- `downloads/curve41417-20140706.pdf`
