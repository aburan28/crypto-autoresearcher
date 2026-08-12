---
id: KN-LIT-2628
type: literature
title: "Authenticated Encryption with Key Identification"
authors:
  - "Julia Len"
  - "Paul Grubbs"
  - "Thomas Ristenpart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Authenticated encryption with associated data (AEAD) forms the core of much of symmetric cryptography, yet the standard techniques for modeling AEAD assume recipients have no ambiguity about what secret key to use for decryption. This is divorced from what occurs in practice, such as in key management services, where a message recipient can store numerous keys and must identify the correct key before decrypting.

## Key claims (as reported)
- To date there has been no formal investigation of their security properties or efficacy, and the ad hoc solutions for identifying the intended key deployed in practice can be inefficient and, in some cases, vulnerable to practical attacks.
- We provide the first formalization of nonce-based AEAD that supports key identification (AEAD-KI).
- Decryption now takes in a vector of secret keys and a ciphertext and must both identify the correct secret key and decrypt the ciphertext.
- We provide new formal security definitions, including new key robustness definitions and indistinguishability security notions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910199 (1).pdf`
- `downloads/137910199.pdf`
