---
id: KN-LIT-5769
type: literature
title: "Pipelineable On-Line Encryption"
authors:
  - "Farzaneh Abed"
  - "Scott Fluhrer"
  - "Christian Forler"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Correct authenticated decryption requires the receiver to buffer the decrypted message until the authenticity check has been performed. In high-speed networks, which must handle large message frames at low latency, this behavior becomes practically infeasible.

## Key claims (as reported)
- This paper proposes CCA-secure on-line ciphers as a practical alternative to AE schemes since the former provide some defense against malicious message modifications.
- Unfortunately, all published on-line ciphers so far are either inherently sequential, or lack a CCA-security proof.
- This paper introduces POE, a family of on-line ciphers that combines provable security against chosen-ciphertext attacks with pipelineability to support efficient implementations.
- POE combines a block cipher and an ǫ-AXU family of hash functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400159 (1).pdf`
- `downloads/85400159 (2).pdf`
- `downloads/85400159 (3).pdf`
- `downloads/85400159.pdf`
