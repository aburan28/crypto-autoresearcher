---
id: KN-LIT-1440
type: literature
title: "On the UC-(In)Security of PAKE Protocols Without the Random Oracle Model"
authors:
  - "Naman Kumar∗"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/998"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/998"
tags: [hash, mpc, pairing, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A Password-Authenticated Key Exchange (PAKE) protocol allows two parties to jointly establish a shared cryptographic key, where the only information shared in advance is a low-entropy password. The first efficient PAKE protocol whose security does not rely on the random oracle model is the one by Katz, Ostrovsky and Yung (KOY, EUROCRYPT 2001).

## Key claims (as reported)
- Unfortunately, the KOY protocol has only been proven secure in the game-based setting, and it is unclear whether KOY is secure in the stronger Universal Composability (UC) framework, which is the current security standard for PAKE.
- In this work, we present a thorough study of the UC-security of KOY.
- Our contributions are two-fold: 1.
- We formally prove that the KOY protocol is not UC-secure; 2.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-998.pdf`
