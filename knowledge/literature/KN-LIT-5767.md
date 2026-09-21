---
id: KN-LIT-5767
type: literature
title: "Piccolo: An Ultra-Lightweight Blockcipher Kyoji Shibutani, Takanori Isobe, Harunaga Hiwatari, Atsushi Mitsuda"
authors:
  - "Toru Akishita"
  - "Taizo Shirai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new 64-bit blockcipher Piccolo supporting 80 and 128-bit keys. Adopting several novel design and implementation techniques, Piccolo achieves both high security and notably compact implementation in hardware.

## Key claims (as reported)
- We show that Piccolo offers a sufficient security level against known analyses including recent related-key differential attacks and meet-in-the-middle attacks.
- In our smallest implementation, the hardware requirements for the 80 and the 128-bit key mode are only 683 and 758 gate equivalents, respectively.
- Moreover, Piccolo requires only 60 additional gate equivalents to support the decryption function due to its involution structure.
- Furthermore, its efficiency on the energy consumption which is evaluated by energy per bit is also remarkable.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170343 (1).pdf`
- `downloads/69170343 (2).pdf`
- `downloads/69170343 (3).pdf`
- `downloads/69170343.pdf`
