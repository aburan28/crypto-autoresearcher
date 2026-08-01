---
id: KN-LIT-6269
type: literature
title: "Revisiting the IDEA Philosophy"
authors:
  - "Pascal Junod"
  - "Marco Macchetti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since almost two decades, the block cipher IDEA has resisted an exceptional number of cryptanalysis attempts. At the time of writing, the best published attack works against 6 out of the 8.5 rounds (in the non-related-key attacks model), employs almost the whole codebook, and improves the complexity of an exhaustive key search by a factor of only two.

## Key claims (as reported)
- In a parallel way, Lipmaa demonstrated that IDEA can benefit from SIMD (Single Instruction, Multiple Data) instructions on high-end CPUs, resulting in very fast implementations.
- The aim of this paper is two-fold: first, we describe a parallel, time-constant implementation of eight instances of IDEA able to encrypt in counter mode at a speed of 5.42 cycles/byte on an Intel Core2 processor.
- This is comparable to the fastest stream ciphers and notably faster than the best known implementations of most block ciphers on the same processor.
- Second, we propose the design of a new block cipher, named WIDEA, leveraging on IDEA’s outstanding security-performance ratio.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650287 (1).pdf`
- `downloads/56650287 (2).pdf`
- `downloads/56650287 (3).pdf`
- `downloads/56650287.pdf`
