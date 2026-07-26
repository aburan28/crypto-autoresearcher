---
id: KN-LIT-4291
type: literature
title: "How to Maximize Software Performance of Symmetric Primitives on Pentium III and 4 Processors"
authors:
  - "Mitsuru Matsui"
  - "Sayaka Fukuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper discusses the state-of-the-art software optimization methodology for symmetric cryptographic primitives on Pentium III and 4 processors. We aim at maximizing speed by considering the internal pipeline architecture of these processors.

## Key claims (as reported)
- This is the first paper studying an optimization of ciphers on Prescott, a new core of Pentium 4.
- Our AES program with 128-bit key achieves 251 cycles/block on Pentium 4, which is, to our best knowledge, the fastest implementation of AES on Pentium 4.
- We also optimize SNOW2.0 keystream generator.
- Our program of SNOW2.0 for Pentium III runs at the rate of 2.75 μops/cycle, which seems the most efficient code ever made for a real-world cipher primitive.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/35570387 (1).pdf`
- `downloads/35570387 (2).pdf`
- `downloads/35570387 (3).pdf`
- `downloads/35570387.pdf`
