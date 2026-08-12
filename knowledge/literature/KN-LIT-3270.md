---
id: KN-LIT-3270
type: literature
title: "Cryptanalysis of the LAKE Hash Family"
authors:
  - "Alex Biryukov"
  - "Praveen Gauravaram"
  - "Jian Guo"
  - "Dmitry Khovratovich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We analyse the security of the cryptographic hash function LAKE-256 proposed at FSE 2008 by Aumasson, Meier and Phan. By exploiting non-injectivity of some of the building primitives of LAKE, we show three different collision and near-collision attacks on the compression function.

## Key claims (as reported)
- The first attack uses differences in the chaining values and the block counter and finds collisions with complexity 233 .
- The second attack utilizes differences in the chaining values and salt and yields collisions with complexity 242 .
- The final attack uses differences only in the chaining values to yield near-collisions with complexity 299 .
- All our attacks are independent of the number of rounds in the compression function.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650164 (1).pdf`
- `downloads/56650164 (2).pdf`
- `downloads/56650164 (3).pdf`
- `downloads/56650164.pdf`
