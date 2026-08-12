---
id: KN-LIT-7364
type: literature
title: "Unidirectional Chosen-Ciphertext Secure Proxy Re-Encryption"
authors:
  - "UCL Crypto Group"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 1998, Blaze, Bleumer, and Strauss proposed a cryptographic primitive called proxy re-encryption, in which a proxy transforms – without seeing the corresponding plaintext – a ciphertext computed under Alice’s public key into one that can be opened using Bob’s secret key. Recently, an appropriate definition of chosen-ciphertext security and a construction fitting this model were put forth by Canetti and Hohenberger.

## Key claims (as reported)
- Their system is bidirectional : the information released to divert ciphertexts from Alice to Bob can also be used to translate ciphertexts in the opposite direction.
- In this paper, we present the first construction of unidirectional proxy re-encryption scheme with chosenciphertext security in the standard model (i.e. without relying on the random oracle idealization), which solves a problem left open at CCS’07.
- Our construction is efficient and requires a reasonable complexity assumption in bilinear map groups.
- Like the Canetti-Hohenberger scheme, it ensures security according to a relaxed definition of chosen-ciphertext introduced by Canetti, Krawczyk and Nielsen.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49390363 (1).pdf`
- `downloads/49390363 (2).pdf`
- `downloads/49390363 (3).pdf`
- `downloads/49390363.pdf`
