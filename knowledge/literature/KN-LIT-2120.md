---
id: KN-LIT-2120
type: literature
title: "A Modular Treatment of Cryptographic APIs: The Symmetric-Key Case"
authors:
  - "Thomas Shrimpton"
  - "Martijn Stam"
  - "Bogdan Warinschi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Application Programming Interfaces (APIs) to cryptographic tokens like smartcards and Hardware Security Modules (HSMs) provide users with commands to manage and use cryptographic keys stored on trusted hardware. Their design is mainly guided by industrial standards with only informal security promises.

## Key claims (as reported)
- In this paper we propose cryptographic models for the security of such APIs.
- The key feature of our approach is that it enables modular analysis.
- Specifically, we show that a secure cryptographic API can be obtained by combining a secure API for key-management together with secure implementations of, for instance, encryption or message authentication.
- Our models are the first to provide such compositional guarantees while considering realistic adversaries that can adaptively corrupt keys stored on tokens.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140271 (1).pdf`
- `downloads/98140271.pdf`
