---
id: KN-LIT-4175
type: literature
title: "HBS: A Single-Key Mode of Operation for Deterministic Authenticated Encryption"
authors:
  - "Tetsu Iwata"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose the HBS (Hash Block Stealing) mode of operation. This is the first single-key mode that provably achieves the goal of providing deterministic authenticated encryption.

## Key claims (as reported)
- The authentication part of HBS utilizes a newly-developed, vector-input polynomial hash function.
- The encryption part uses a blockcipher-based, counter-like mode.
- These two parts are combined in such a way as the numbers of finite-field multiplications and blockcipher calls are minimized.
- Specifically, for a header of h blocks and a message of m blocks, the HBS algorithm requires just h + m + 2 multiplications in the finite field and m + 2 calls to the blockcipher.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650405 (1).pdf`
- `downloads/56650405 (2).pdf`
- `downloads/56650405 (3).pdf`
- `downloads/56650405.pdf`
