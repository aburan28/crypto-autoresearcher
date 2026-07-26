---
id: KN-LIT-4233
type: literature
title: "Homomorphic Evaluation of the AES Circuit"
authors:
  - "Craig Gentry"
  - "Shai Halevi"
  - "Nigel P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, mpc, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a working implementation of leveled homomorphic encryption (without bootstrapping) that can evaluate the AES-128 circuit in three different ways. One variant takes under over 36 hours to evaluate an entire AES encryption operation, using NTL (over GMP) as our underlying software platform, and running on a large-memory machine.

## Key claims (as reported)
- Using SIMD techniques, we can process over 54 blocks in each evaluation, yielding an amortized rate of just under 40 minutes per block.
- Another implementation takes just over two and a half days to evaluate the AES operation, but can process 720 blocks in each evaluation, yielding an amortized rate of just over five minutes per block.
- We also detail a third implementation, which theoretically could yield even better amortized complexity, but in practice turns out to be less competitive.
- For our implementations we develop both AES-specific optimizations as well as several “generic” tools for FHE evaluation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170845 (1).pdf`
- `downloads/74170845 (2).pdf`
- `downloads/74170845 (3).pdf`
- `downloads/74170845.pdf`
