---
id: KN-LIT-2542
type: literature
title: "Anonymous AE"
authors:
  - "John Chan"
  - "Phillip Rogaway"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The customary formulation of authenticated encryption (AE) requires the decrypting party to supply the correct nonce with each ciphertext it decrypts. To enable this, the nonce is often sent in the clear alongside the ciphertext.

## Key claims (as reported)
- But doing this can forfeit anonymity and degrade usability.
- Anonymity can also be lost by transmitting associated data (AD) or a session-ID (used to identify the operative key).
- To address these issues, we introduce anonymous AE, wherein ciphertexts must conceal their origin even when they are understood to encompass everything needed to decrypt (apart from the receiver’s secret state).
- We formalize a type of anonymous AE we call anAE, anonymous noncebased AE, which generalizes and strengthens conventional nonce-based AE, nAE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210383 (1).pdf`
- `downloads/119210383.pdf`
