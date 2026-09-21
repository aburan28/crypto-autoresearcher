---
id: KN-LIT-6796
type: literature
title: "Statistical Decoding 2.0: Reducing Decoding to LPN"
authors:
  - "Jean-Pierre Tillich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security of code-based cryptography relies primarily on the hardness of generic decoding with linear codes. The best generic decoding algorithms are all improvements of an old algorithm due to Prange: they are known under the name of information set decoders (ISD).

## Key claims (as reported)
- A while ago, a generic decoding algorithm which does not belong to this family was proposed: statistical decoding.
- It is a randomized algorithm that requires the computation of a large set of parity-checks of moderate weight, and uses some kind of majority voting on these equations to recover the error.
- This algorithm was long forgotten because even the best variants of it performed poorly when compared to the simplest ISD algorithm.
- We revisit this old algorithm by using parity-check equations in a more general way.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910327 (1).pdf`
- `downloads/137910327.pdf`
