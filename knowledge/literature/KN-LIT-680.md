---
id: KN-LIT-680
type: literature
title: "Improved Meet-in-the-Middle Preimage Attacks against AES Hashing Modes"
authors:
  - "Zhenzhen Bao"
  - "Lin Ding"
  - "Jian Guo"
  - "Haoyang Wang"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/607"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/607"
tags: [cryptanalysis, hash, mov-fr, pairing, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Hashing modes are ways to convert a block cipher into a hash function, and those with AES as the underlying block cipher are referred to as AES hashing modes. Sasaki in 2011, introduced the first preimage attack against AES hashing modes with the AES block cipher reduced to 7 rounds, by the method of meet-in-the-middle.

## Key claims (as reported)
- In his attack, the key-schedules are not taken into account.
- Hence, the same attack applies to all three versions of AES.
- In this paper, by introducing neutral bits from the key, extra degree of freedom is gained, which is utilized in two ways, i.e., to reduce the time complexity and to extend the attack to more rounds.
- As an immediate result, the complexities of 7-round pseudo-preimage attacks are reduced from 2120 to 2104 , 296 , and 296 for AES-128, AES-192, and AES-256, respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-607.pdf`
