---
id: KN-LIT-5722
type: literature
title: "Parallelizable and"
authors:
  - "Elmar Tischhauser"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Online ciphers encrypt an arbitrary number of plaintext blocks and output ciphertext blocks which only depend on the preceding plaintext blocks. All online ciphers proposed so far are essentially serial, which significantly limits their performance on parallel architectures such as modern general-purpose CPUs or dedicated hardware.

## Key claims (as reported)
- We propose the first parallelizable online cipher, COPE.
- It performs two calls to the underlying block cipher per plaintext block and is fully parallelizable in both encryption and decryption.
- COPE is proven secure against chosenplaintext attacks assuming the underlying block cipher is a strong PRP.
- We then extend COPE to create COPA, the first parallelizable, online authenticated cipher with nonce-misuse resistance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82710318 (1).pdf`
- `downloads/82710318 (2).pdf`
- `downloads/82710318 (3).pdf`
- `downloads/82710318.pdf`
