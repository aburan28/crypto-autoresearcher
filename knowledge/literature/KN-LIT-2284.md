---
id: KN-LIT-2284
type: literature
title: "A Very Compact S-box for AES"
authors:
  - "D. Canright"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A key step in the Advanced Encryption Standard (AES) algorithm is the “S-box.” Many implementations of AES have been proposed, for various goals, that effect the S-box in various ways. In particular, the most compact implementations to date of Satoh et al.[1] and Mentens et al.[2] perform the 8-bit Galois field inversion of the S-box using subfields of 4 bits and of 2 bits.

## Key claims (as reported)
- Our work refines this approach to achieve a more compact S-box.
- We examined many choices of basis for each subfield, not only polynomial bases as in previous work, but also normal bases, giving 432 cases.
- The isomorphism bit matrices are fully optimized, improving on the “greedy algorithm.” Introducing some NOR gates gives further savings.
- The best case improves on [1] by 20%.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/032 (1).pdf`
- `downloads/032 (2).pdf`
- `downloads/032 (3).pdf`
- `downloads/032.pdf`
