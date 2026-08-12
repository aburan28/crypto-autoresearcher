---
id: KN-LIT-4304
type: literature
title: "How to Securely Release Unverified Plaintext in Authenticated Encryption"
authors:
  - "Nicky Mouha"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, protocol, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Scenarios in which authenticated encryption schemes output decrypted plaintext before successful verification raise many security issues. These situations are sometimes unavoidable in practice, such as when devices have insufficient memory to store an entire plaintext, or when a decrypted plaintext needs early processing due to real-time requirements.

## Key claims (as reported)
- We introduce the first formalization of the releasing unverified plaintext (RUP) setting.
- To achieve privacy, we propose using plaintext awareness (PA) along with IND-CPA.
- An authenticated encryption scheme is PA if it has a plaintext extractor, which tries to fool adversaries by mimicking the decryption oracle, without the secret key.
- Releasing unverified plaintext to the attacker then becomes harmless as it is infeasible to distinguish the decryption oracle from the plaintext extractor.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730329 (1).pdf`
- `downloads/88730329 (2).pdf`
- `downloads/88730329 (3).pdf`
- `downloads/88730329.pdf`
