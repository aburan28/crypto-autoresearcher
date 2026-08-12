---
id: KN-LIT-3252
type: literature
title: "Cryptanalysis of Reduced NORX"
authors:
  - "Nasour Bagheri"
  - "Tao Huang"
  - "Keting Jia"
  - "Florian Mendel"
  - "Yu Sasaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NORX is a second round candidate of the ongoing CAESAR competition for authenticated encryption. It is a nonce based authenticated encryption scheme based on the sponge construction.

## Key claims (as reported)
- Its two variants denoted by NORX32 and NORX64 provide a security level of 128 and 256 bits, respectively.
- In this paper, we present a state/key recovery attack for both variants with the number of rounds of the core permutation reduced to 2 (out of 4) rounds.
- The time and data complexities of the attack for NORX32 are 2119 and 266 respectively, and for NORX64 are 2234 and 2132 respectively, while the memory complexity is negligible.
- Furthermore, we show a state recovery attack against NORX in the parallel mode using an internal differential attack for 2 rounds of the permutation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830528 (1).pdf`
- `downloads/97830528.pdf`
