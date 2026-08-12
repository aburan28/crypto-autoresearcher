---
id: KN-LIT-6253
type: literature
title: "Reverse-Engineering the S-Box of Streebog"
authors:
  - "STRIBOBr ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, hash, implementation, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Russian Federation’s standardization agency has recently published a hash function called Streebog and a 128-bit block cipher called Kuznyechik. Both of these algorithms use the same 8-bit S-Box but its design rationale was never made public.

## Key claims (as reported)
- In this paper, we reverse-engineer this S-Box and reveal its hidden structure.
- It is based on a sort of 2-round Feistel Network where exclusive-or is replaced by a finite field multiplication.
- This structure is hidden by two different linear layers applied before and after.
- In total, five different 4-bit S-Boxes, a multiplexer, two 8-bit linear permutations and two finite field multiplications in a field of size 24 are needed to compute the S-Box.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650135 (1).pdf`
- `downloads/96650135.pdf`
