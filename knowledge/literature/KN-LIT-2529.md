---
id: KN-LIT-2529
type: literature
title: "Analysis of the Kupyna-256 Hash Function"
authors:
  - "Christoph Dobraunig"
  - "Maria Eichlseder"
  - "Florian Mendel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hash function Kupyna was recently published as the Ukrainian standard DSTU 7564:2014. It is structurally very similar to the SHA-3 finalist Grøstl, but differs in details of the round transformations.

## Key claims (as reported)
- Most notably, some of the round constants are added with a modular addition, rather than bitwise xor.
- This change prevents a straightforward application of some recent attacks, in particular of the rebound attacks on the compression function of similar AES-like hash constructions.
- However, we show that it is actually possible to mount rebound attacks, despite the presence of modular constant additions.
- More specifically, we describe collision attacks on the compression function for 6 (out of 10) rounds of Kupyna-256 with an attack complexity of 270 , and for 7 rounds with complexity 2125.8 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830548 (1).pdf`
- `downloads/97830548.pdf`
