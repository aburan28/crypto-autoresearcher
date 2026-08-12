---
id: KN-LIT-5236
type: literature
title: "Nonce-Based Symmetric Encryption"
authors:
  - "Phillip Rogaway"
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
Symmetric encryption schemes are usually formalized so as to make the encryption operation a probabilistic or state-dependent function E of the message M and the key K: the user supplies M and K and the encryption process does the rest, flipping coins or modifying internal state in order to produce a ciphertext C. Here we investigate an alternative syntax for an encryption scheme, where the encryption process E is a deterministic function that surfaces an initialization vector (IV).

## Key claims (as reported)
- The user supplies a message M , key K, and initialization vector N , getting N back the (one and only) associated ciphertext C = EK (M ).
- We concentrate on the case where the IV is guaranteed to be a nonce—something that takes on a new value with every message one encrypts.
- We explore definitions, constructions, and properties for nonce-based encryption.
- Symmetric encryption with a surfaced IV more directly captures real-word constructions like CBC mode, and encryption schemes constructed to be secure under nonce-based security notions may be less prone to misuse.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170349 (1).pdf`
- `downloads/30170349 (2).pdf`
- `downloads/30170349.pdf`
