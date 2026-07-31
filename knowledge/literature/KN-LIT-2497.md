---
id: KN-LIT-2497
type: literature
title: "An Improved Impossible Differential Attack on MISTY1"
authors:
  - "Orr Dunkelman"
  - "Nathan Keller"
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
MISTY1 is a Feistel block cipher that received a great deal of cryptographic attention. Its recursive structure, as well as the added FL layers, have been successful in thwarting various cryptanalytic techniques.

## Key claims (as reported)
- The best known attacks on reduced variants of the cipher are on either a 4-round variant with the FL functions, or a 6-round variant without the FL functions (out of the 8 rounds of the cipher).
- In this paper we combine the generic impossible differential attack against 5-round Feistel ciphers with the dedicated Slicing attack to mount an attack on 5-round MISTY1 with all the FL functions with time complexity of 246.45 simple operations.
- We then extend the attack to 6round MISTY1 with the FL functions present, leading to the best known cryptanalytic result on the cipher.
- We also present an attack on 7-round MISTY1 without the FL layers.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500447 (1).pdf`
- `downloads/53500447 (2).pdf`
- `downloads/53500447 (3).pdf`
- `downloads/53500447.pdf`
