---
id: KN-LIT-849
type: literature
title: "Complete Practical Side-Channel-Assisted Reverse Engineering of AES-Like Ciphers"
authors:
  - "Andrea Caforio"
  - "Fatih Balli"
  - "Subhadeep Banik"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1252"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1252"
tags: [cryptanalysis, pairing, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Public knowledge about the structure of a cryptographic system is a standard assumption in the literature and algorithms are expected to guarantee security in a setting where only the encryption key is kept secret. Nevertheless, undisclosed proprietary cryptographic algorithms still find widespread use in applications both in the civil and military domains.

## Key claims (as reported)
- Even though side-channel-based reverse engineering attacks that recover the hidden components of custom cryptosystems have been demonstrated for a wide range of constructions, the complete and practical reverse engineering of AES-128-like ciphers remains unattempted.
- In this work, we close this gap and propose the first practical reverse engineering of AES-128-like custom ciphers, i.e., algorithms that deploy undisclosed SubBytes, ShiftRows and MixColumns functions.
- By performing a side-channel-assisted differential power analysis, we show that the amount of traces required to fully recover the undisclosed components are relatively small, hence the possibility of a side-channel attack remains as a practical threat.
- The results apply to both 8-bit and 32-bit architectures and were validated on two common microcontroller platforms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1252.pdf`
