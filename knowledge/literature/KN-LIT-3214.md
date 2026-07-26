---
id: KN-LIT-3214
type: literature
title: "Cryptanalysis of 3-pass HAVAL?"
authors:
  - "Bart Van Rompay"
  - "Alex Biryukov"
  - "Bart Preneel"
  - "Joos Vandewalle"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, provable-security, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
HAVAL is a cryptographic hash function proposed in 1992 by Zheng, Pieprzyk and Seberry. Its has a structure that is quite similar to other well-known hash functions such as MD4 and MD5.

## Key claims (as reported)
- The specification of HAVAL includes a security parameter: the number of passes (that is, the number of times that a particular word of the message is used in the computation) can be chosen equal to 3, 4 or 5.
- In this paper we describe a practical attack that finds collisions for the 3-pass version of HAVAL.
- This means that it is possible to generate pairs of messages hashing to the same value.
- The computational complexity of the attack corresponds to about 229 computations of the compression function of 3-pass HAVAL; the required amount of memory is negligible.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/28940215 (1).pdf`
- `downloads/28940215 (2).pdf`
- `downloads/28940215.pdf`
