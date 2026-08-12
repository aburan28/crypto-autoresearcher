---
id: KN-LIT-2378
type: literature
title: "ALE: AES-Based Lightweight Authenticated Encryption Andrey Bogdanov1 , Florian Mendel2 , Francesco Regazzoni3,4"
authors:
  - "Vincent Rijmen"
  - "Elmar Tischhauser"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a new Authenticated Lightweight E ncryption algorithm coined ALE. The basic operation of ALE is the AES round transformation and the AES-128 key schedule.

## Key claims (as reported)
- ALE is an online single-pass authenticated encryption algorithm that supports optional associated data.
- Its security relies on using nonces.
- We provide an optimized low-area implementation of ALE in ASIC hardware and demonstrate that its area is about 2.5 kGE which is almost two times smaller than that of the lightweight implementations for AES-OCB and ASC-1 using the same lightweight AES engine.
- At the same time, it is at least 2.5 times more performant than the alternatives in their smallest implementations by requiring only about 4 AES rounds to both encrypt and authenticate a 128-bit data block for longer messages.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240416 (1).pdf`
- `downloads/84240416 (2).pdf`
- `downloads/84240416 (3).pdf`
- `downloads/84240416.pdf`
