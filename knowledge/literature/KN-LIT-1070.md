---
id: KN-LIT-1070
type: literature
title: "All You Need Is Fault: Zero-Value Attacks on AES and a New λ-Detection M&M"
authors:
  - "Haruka Hirata"
  - "Daiki Miyahara"
  - "Victor Arribas"
  - "Yang Li"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1129"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1129"
tags: [cryptanalysis, implementation, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Deploying cryptography on embedded systems requires security against physical attacks. At CHES 2019, M&M was proposed as a combined countermeasure applying masking against SCAs and information-theoretic MAC tags against FAs.

## Key claims (as reported)
- In this paper, we show that one of the protected AES implementations in the M&M paper is vulnerable to a zero-value SIFA2-like attack.
- A practical attack is demonstrated on an ASIC board.
- We propose two versions of the attack: the first follows the SIFA approach to inject faults in the last round, while the second one is an extension of SIFA and FTA but applied to the first round with chosen plaintext.
- The two versions work at the byte level, but the latter version considerably improves the efficiency of the attack.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-1129.pdf`
