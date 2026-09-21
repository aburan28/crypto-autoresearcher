---
id: KN-LIT-2106
type: literature
title: "A MAC Mode for Lightweight Block Ciphers"
authors:
  - "Atul Luykx"
  - "Bart Preneel"
  - "Elmar Tischhauser"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lightweight cryptography strives to protect communication in constrained environments without sacrificing security. However, security often conflicts with efficiency, shown by the fact that many new lightweight block cipher designs have block sizes as low as 64 or 32 bits.

## Key claims (as reported)
- Such low block sizes lead to impractical limits on how much data a mode of operation can process per key.
- MAC (message authentication code) modes of operation frequently have bounds which degrade with both the number of messages queried and the message length.
- We present a MAC mode of operation, LightMAC, where the message length has no effect on the security bound, allowing an order of magnitude more data to be processed per key.
- Furthermore, LightMAC is incredibly simple, has almost no overhead over the block cipher, and is parallelizable.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830041 (1).pdf`
- `downloads/97830041.pdf`
