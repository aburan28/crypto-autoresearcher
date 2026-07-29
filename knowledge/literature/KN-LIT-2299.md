---
id: KN-LIT-2299
type: literature
title: "Accelerating AES with Vector Permute Instructions"
authors:
  - "Mike Hamburg"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We demonstrate new techniques to speed up the Rijndael (AES) block cipher using vector permute instructions. Because these techniques avoid data- and key-dependent branches and memory references, they are immune to known timing attacks.

## Key claims (as reported)
- This is the first constant-time software implementation of AES which is efficient for sequential modes of operation.
- This work can be adapted to several other primitives using the AES S-box such as the stream cipher LEX, the block cipher Camellia and the hash function Fugue.
- We focus on Intel’s SSSE3 and Motorola’s Altivec, but our techniques can be adapted to other systems with vector permute instructions, such as the IBM Xenon and Cell processors, the ARM Cortex series and the forthcoming AMD “Bulldozer” core.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470016 (1).pdf`
- `downloads/57470016 (2).pdf`
- `downloads/57470016 (3).pdf`
- `downloads/57470016.pdf`
