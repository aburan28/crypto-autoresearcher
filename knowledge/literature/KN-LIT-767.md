---
id: KN-LIT-767
type: literature
title: "Fixslicing AES-like Ciphers New bitsliced AES speed records on ARM-Cortex M and RISC-V"
authors:
  - "Alexandre Adomnicăi"
  - "Thomas Peyrin"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1123"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1123"
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The fixslicing implementation strategy was originally introduced as a new representation for the hardware-oriented GIFT block cipher to achieve very efficient software constant-time implementations. In this article, we show that the fundamental idea underlying the fixslicing technique is not of interest only for GIFT, but can be applied to other ciphers as well.

## Key claims (as reported)
- Especially, we study the benefits of fixslicing in the case of AES and show that it allows to reduce by 52% the amount of operations required by the linear layer when compared to the current fastest bitsliced implementation on 32-bit platforms.
- Overall, we report that fixsliced AES-128 allows to reach 80 and 87 cycles per byte on ARM Cortex-M and E31 RISC-V processors respectively (assuming pre-computed round keys), improving the previous records on those platforms by 21% and 30%.
- In order to highlight that our work also directly improves masked implementations that rely on bitslicing, we report implementation results when integrating first-order masking that outperform by 12% the fastest results reported in the literature on ARM Cortex-M4.
- Finally, we demonstrate the genericity of the fixslicing technique for AES-like designs by applying it to the Skinny-128 tweakable block ciphers.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-1123.pdf`
