---
id: KN-LIT-1717
type: literature
title: "Local Constraints Behind Fourier Analysis of Neural Distinguishers for SPECK32/64"
authors:
  - "Yunjae Hwang"
  - "Sunyeop Kim"
  - "Hanbeom Shin"
  - "Deukjo Hong"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1136"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1136"
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Neural distinguishers for ARX ciphers can exploit information beyond classical difference distributions and several interpretability frameworks have been proposed. In this paper, we study two frameworks for SPECK32/64 by connecting their viewpoints: local constraints of modular addition and Fourier analysis of trained neural distinguishers.

## Key claims (as reported)
- We show that the dominant Fourier parities of a raw-pair differential neural distinguisher can be rewritten in the local variables associated with the last modular addition.
- This representation separates value-dependent variant differentiallinear terms from difference-dependent traditional terms, and explains their biases through specific local constraints and branch effects.
- We further extend the analysis to a boomerang right-quartet setting.
- We construct a neural distinguisher whose input is only the original ciphertext pair, while positive and negative samples are matched with respect to the observed ciphertext difference.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1136.pdf`
