---
id: KN-LIT-2039
type: literature
title: "A Failure-Friendly Design Principle for Hash Functions"
authors:
  - "Stefan Lucks"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper reconsiders the established Merkle-Damgård design principle for iterated hash functions. The internal state size w of an iterated n-bit hash function is treated as a security parameter of its own right.

## Key claims (as reported)
- In a formal model, we show that increasing w quantifiably improves security against certain attacks, even if the compression function fails to be collision resistant.
- We propose the wide-pipe hash, internally using a w-bit compression function, and the double-pipe hash, with w = 2n and an n-bit compression function used twice in parallel.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/472 (1).pdf`
- `downloads/472 (2).pdf`
- `downloads/472 (3).pdf`
- `downloads/472.pdf`
