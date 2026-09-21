---
id: KN-LIT-1645
type: literature
title: "Exploiting Strong Key Bridges: Full-Fledged"
authors:
  - "Lei WangB"
  - "Lei Hu"
  - "Jian Weng"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1110"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1110"
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The TWEAKEY framework provides a generic construction for designing tweakable block ciphers. Prominent instances are Deoxys-BC and SKINNY, which have been standardized by ISO/IEC.

## Key claims (as reported)
- In this paper, we analyze the tweakey schedules of these ciphers and identify strong dependencies between certain subtweakeys, which we call strong key bridges.
- We then exploit these dependencies in rectangle attacks under the related-tweakey setting.
- Moreover, we develop a comprehensive constraint programming model to search for rectangle attacks.
- Our model not only unifies the distinguisher and the key-recovery part while permitting arbitrary key-guessing strategies, but also integrates three new components, i.e., the statetest technique, explicit last-step computation, and the strong key bridges.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1110.pdf`
