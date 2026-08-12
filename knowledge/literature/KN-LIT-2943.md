---
id: KN-LIT-2943
type: literature
title: "Collision Attacks on the Reduced Dual-Stream Hash Function RIPEMD-128"
authors:
  - "Florian Mendel"
  - "Tomislav Nad"
  - "Martin Schläffer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we analyze the security of RIPEMD-128 against collision attacks. The ISO/IEC standard RIPEMD-128 was proposed 15 years ago and may be used as a drop-in replacement for 128-bit hash functions like MD5.

## Key claims (as reported)
- Only few results have been published for RIPEMD-128, the best being a preimage attack for the first 33 steps of the hash function with complexity 2124.5 .
- In this work, we provide a new assessment of the security margin of RIPEMD-128 by showing attacks on up to 48 (out of 64) steps of the hash function.
- We present a collision attack reduced to 38 steps and a near-collisions attack for 44 steps, both with practical complexity.
- Furthermore, we show non-random properties for 48 steps of the RIPEMD-128 hash function, and provide an example for a collision on the compression function for 48 steps.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490228 (1).pdf`
- `downloads/75490228 (2).pdf`
- `downloads/75490228 (3).pdf`
- `downloads/75490228.pdf`
