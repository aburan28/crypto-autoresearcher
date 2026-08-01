---
id: KN-LIT-1207
type: literature
title: "Breaking the IEEE Encryption Standard – XCB-AES in Two Queries"
authors:
  - "Amit Singh Bhati"
  - "Elena Andreeva ID"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1554"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1554"
tags: [cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Tweakable enciphering modes (TEMs) provide security in various storage and space-critical applications, including disk and filebased encryption and packet-based communication protocols. XCB-AES (originally introduced as XCBv2) is specified in the IEEE 1619.2 standard for encryption of sector-oriented storage media and comes with a formal security proof for block-aligned messages.

## Key claims (as reported)
- In this work, we present the first plaintext recovery attack on XCB-AES – the shared difference attack, demonstrating that the security of XCB-AES is fundamentally flawed.
- Our plaintext recovery attack is highly efficient and requires only two queries (one enciphering and one deciphering), breaking the claimed vil-stprp, stprp as well as the basic sprp security.
- Our shared difference attack exploits an inherent property of polynomial hash functions called separability.
- We pinpoint the exact flaw in the security proof of XCB-AES, which arises from the separability of polynomial hash functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1554.pdf`
