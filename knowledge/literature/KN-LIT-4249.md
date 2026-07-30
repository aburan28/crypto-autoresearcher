---
id: KN-LIT-4249
type: literature
title: "How Far Can We Go on the x64 Processors?"
authors:
  - "Mitsuru Matsui"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper studies the state-of-the-art software optimization methodology for symmetric cryptographic primitives on the new 64-bit x64 processors, AMD Athlon64 (AMD64) and Intel Pentium 4 (EM64T). We fully utilize newly introduced 64-bit registers and instructions for extracting maximal performance of target primitives.

## Key claims (as reported)
- Our program of AES with 128-bit key runs in 170 cycles/block on Athlon 64, which is, as far as we know, the fastest implementation of AES on a PC processor.
- Also we implemented a “bitsliced” AES and Camellia for the first time, both of which achieved very good performance.
- A bitslice implementation is important from the viewpoint of a countermeasure against cache timing attacks because it does not require lookup tables with a keydependent address.
- We also analyze performance of SHA256/512 and Whirlpool hash functions and show that SHA512 can run faster than SHA256 on Athlon 64.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40470344 (1).pdf`
- `downloads/40470344 (2).pdf`
- `downloads/40470344 (3).pdf`
- `downloads/40470344.pdf`
