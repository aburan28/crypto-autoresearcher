---
id: KN-LIT-6969
type: literature
title: "The EAX Mode of Operation"
authors:
  - "Mihir Bellare"
  - "Phillip Rogaway"
  - "David Wagner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a block-cipher mode of operation, EAX, for solving the problem of authenticated-encryption with associated-data (AEAD). Given a nonce N , a message M , and a header H , our mode protects the privacy of M and the authenticity of both M and H .

## Key claims (as reported)
- Strings N , M , and H are arbitrary bit strings, and the mode uses 2 M =n + H =n + N =n block-cipher calls when these strings are nonempty and n is the block length of the underlying block cipher.
- Among EAX’s characteristics are that it is on-line (the length of a message isn’t needed to begin processing it) and a fixed header can be pre-processed, effectively removing the per-message cost of binding it to the ciphertext. dj j e dj j e dj j e

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170391 (1).pdf`
- `downloads/30170391 (2).pdf`
- `downloads/30170391.pdf`
