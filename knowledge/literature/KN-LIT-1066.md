---
id: KN-LIT-1066
type: literature
title: "A Systematic Study of Data Augmentation for Protected AES Implementations"
authors:
  - "Huimin Li"
  - "Guilherme Perin"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1179"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1179"
tags: [implementation, mov-fr, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Side-channel attacks against cryptographic implementations are mitigated by the application of masking and hiding countermeasures. Hiding countermeasures attempt to reduce the Signal-to-Noise Ratio of measurements by adding noise or desynchronization effects during the execution of the cryptographic operations.

## Key claims (as reported)
- To bypass these protections, attackers adopt signal processing techniques such as pattern alignment, filtering, averaging, or resampling.
- Convolutional neural networks have shown the ability to reduce the effect of countermeasures without the need for trace preprocessing, especially alignment, due to their shift invariant property.
- Data augmentation techniques are also considered to improve the regularization capacity of the network, which improves generalization and, consequently, reduces the attack complexity.
- In this work, we deploy systematic experiments to investigate the benefits of data augmentation techniques against masked AES implementations when they are also protected with hiding countermeasures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1179.pdf`
