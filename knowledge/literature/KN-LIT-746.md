---
id: KN-LIT-746
type: literature
title: "Differential Power Analysis Attacks on Different Implementations of AES with the ChipWhisperer Nano"
authors:
  - "Leah Lathrop"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1008"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1008"
tags: [cryptanalysis, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Side-channel attacks exploit information that is leaked from hardware. The differential power analysis (DPA) attack aims at extracting sensitive information that is processed by the operations in a cryptographic primitive.

## Key claims (as reported)
- Power traces are collected and subsequently processed using statistical methods.
- The ChipWhisperer Nano is a low-cost, open-source device that can be used to implement and study side-channel attacks.
- This paper describes how the DPA attack with the difference of means method can be used to extract the secret key from both an 8-bit and a 32-bit implementation of AES using the ChipWhisperer Nano.
- The results show that although it is possible to carry out the attack on both implementations, the attack on the 32-bit implementation requires more traces than the 8-bit implementation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-1008.pdf`
