---
id: KN-LIT-2931
type: literature
title: "COBRA: A Parallelizable Authenticated Online Cipher without Block Cipher Inverse"
authors:
  - "Elena Andreeva"
  - "Atul Luykx"
  - "Bart Mennink"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new, misuse-resistant scheme for online authenticated encryption, following the framework set forth by Fleischmann et al. Our scheme, COBRA, is roughly as efficient as the GCM mode of operation for nonce-based authenticated encryption, performing one block cipher call plus one finite field multiplication per message block in a parallelizable way.

## Key claims (as reported)
- The major difference from GCM is that COBRA preserves privacy up to prefix under nonce repetition.
- However, COBRA only provides authenticity against nonce-respecting adversaries.
- As compared to COPA (ASIACRYPT 2013), our new scheme requires no block cipher inverse and hence enjoys provable security under a weaker assumption about the underlying block cipher.
- In addition, COBRA can possibly perform better than COPA on platforms where finite field multiplication can be implemented faster than the block cipher in use, since COBRA essentially replaces half of the block cipher calls in COPA with finite field multiplications.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400196 (1).pdf`
- `downloads/85400196 (2).pdf`
- `downloads/85400196 (3).pdf`
- `downloads/85400196.pdf`
