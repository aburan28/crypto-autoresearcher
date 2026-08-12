---
id: KN-LIT-3889
type: literature
title: "Finding Preimages of Tiger Up to 23 Steps"
authors:
  - "Lei Wang"
  - "Yu Sasaki"
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
This paper evaluates the preimage resistance of the Tiger hash function. We will propose a pseudo-preimage attack on its compression function up to 23 steps with a complexity of 2181 , which can be converted to a preimage attack on 23-step Tiger hash function with a complexity of 2187.5 .

## Key claims (as reported)
- The memory requirement of these attacks is 222 words.
- Our pseudo-preimage attack on the Tiger compression function adopts the meet-in-the-middle approach.
- We will divide the computation of the Tiger compression function into two independent parts.
- This enables us to transform the target of finding a pseudo-preimage to another target of finding a collision between two independent sets of some internal state, which will reduce the complexity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470118 (1).pdf`
- `downloads/61470118 (2).pdf`
- `downloads/61470118 (3).pdf`
- `downloads/61470118.pdf`
