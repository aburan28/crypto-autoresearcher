---
id: KN-LIT-1470
type: literature
title: "Side-channel safe conditional moves and swaps"
authors:
  - "David Santos⋆"
  - "Michael Scott"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/935"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/935"
tags: [elliptic-curve, implementation, mov-fr, pairing, protocol, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Constant-time implementations are a cornerstone of secure cryptographic systems, particularly in the context of key exchange protocols and digital signature schemes. These implementations are designed to eliminate timing side-channel vulnerabilities by ensuring that the program’s execution time is independent of secret data.

## Key claims (as reported)
- A fundamental building block for achieving constant-time behavior is the conditional move operation.
- Unlike traditional branching constructs (such as if statements), which may introduce data-dependent timing variations, conditional moves allow developers to write logic that behaves identically at the hardware level regardless of input values.
- As a result, they are widely used in cryptographic libraries and standards to ensure both functional correctness and resistance to timing attacks.
- In this work, we describe our efforts to implement elliptic curve cryptography with some immunity against certain power leakage side-channel attacks, using standard C and Rust code.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-935.pdf`
