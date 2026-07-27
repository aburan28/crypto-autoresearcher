---
id: KN-LIT-3047
type: literature
title: "Computational Wiretap Coding from Indistinguishability Obfuscation"
authors:
  - "Yuval Ishai"
  - "Aayush Jain"
  - "Paul Lou"
  - "Amit Sahai"
  - "Mark Zhandry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A wiretap coding scheme for a pair of noisy channels (ChB, ChE) enables Alice to reliably communicate a message to Bob by sending its encoding over ChB, while hiding the message from an adversary Eve who obtains the same encoding over ChE. A necessary condition for the feasibility of wiretap coding is that ChB is not a degradation of ChE, namely Eve cannot simulate Bob’s view.

## Key claims (as reported)
- While insufficient in the information-theoretic setting, a recent work of Ishai, Korb, Lou, and Sahai (Crypto 2022) showed that the non-degradation condition is sufficient in the computational setting, assuming idealized flavors of obfuscation.
- The question of basing a similar feasibility result on standard cryptographic assumptions was left open, even in simple special cases.
- In this work, we settle the question for all discrete memoryless channels where the (common) input alphabet of ChB and ChE is binary, and with arbitrary finite output alphabet, under standard (sub-exponential) hardness assumptions: namely those assumptions that imply indistinguishability obfuscation (Jain-Lin-Sahai 2021, 2022), and injective PRGs.
- In particular, this establishes the feasibility of computational wiretap coding when ChB is a binary symmetric channel with crossover probability p and ChE is a binary erasure channel with erasure probability e, where e > 2p.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850396 (1).pdf`
- `downloads/140850396.pdf`
