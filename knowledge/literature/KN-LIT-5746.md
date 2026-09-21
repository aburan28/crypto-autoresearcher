---
id: KN-LIT-5746
type: literature
title: "Perfect Block Ciphers With Small Blocks"
authors:
  - "Louis Granboulan"
  - "Thomas Pornin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Existing symmetric encryption algorithms target messages consisting of elementary binary blocks of at least 64 bits. Some applications need a block cipher which operates over smaller and possibly nonbinary blocks, which can be viewed as a pseudo-random permutation of n elements.

## Key claims (as reported)
- We present an algorithm for selecting such a random permutation of n elements and evaluating efficiently the permutation and its inverse over arbitrary inputs.
- We use an underlying deterministic RNG (random number generator).
- Each evaluation of the permutation uses O(log n) space and O((log n)3 ) RNG invocations.
- The selection process is “perfect”: the permutation is uniformly selected among the n! possibilities.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45930457 (1).pdf`
- `downloads/45930457 (2).pdf`
- `downloads/45930457 (3).pdf`
- `downloads/45930457.pdf`
