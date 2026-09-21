---
id: KN-LIT-5731
type: literature
title: "Partial-Collision Attack on the Round-Reduced Compression Function of Skein-256"
authors:
  - "Hongbo Yu"
  - "Jiazhe Chen"
  - "Xiaoyun Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hash function Skein is one of 5 finalists of the NIST SHA-3 competition. It is based on the block cipher Threefish which only uses three primitive operations: modular addition, rotation and bitwise XOR (ARX).

## Key claims (as reported)
- This paper proposes a free-start partial-collision attack on round-reduced Skein-256 by combing the rebound attack with the modular differential techniques.
- The main idea of our attack is to connect two short differential paths into a long one with another differential characteristic that is complicated.
- Following our path, we give a free-start partial-collision attack on Skein-256 reduced to 32 rounds with Hamming distance 50 and complexity about 285 hash computations.
- In particular, we provide practical near-collision examples for Skein-256 reduced to 24 rounds and 28 rounds in the fixed tweaks and choosing tweaks setting separately.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240251 (1).pdf`
- `downloads/84240251 (2).pdf`
- `downloads/84240251 (3).pdf`
- `downloads/84240251.pdf`
