---
id: KN-LIT-260
type: literature
title: "Linearization Framework for Collision Attacks:"
authors:
  - "Application to CubeHash"
year: 2009
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2009/382"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2009/382"
tags: [cryptanalysis, hash, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, an improved differential cryptanalysis framework for finding collisions in hash functions is provided. Its principle is based on linearization of compression functions in order to find low weight differential characteristics as initiated by Chabaud and Joux.

## Key claims (as reported)
- This is formalized and refined however in several ways: for the problem of finding a conforming message pair whose differential trail follows a linear trail, a condition function is introduced so that finding a collision is equivalent to finding a preimage of the zero vector under the condition function.
- Then, the dependency table concept shows how much influence every input bit of the condition function has on each output bit.
- Careful analysis of the dependency table reveals degrees of freedom that can be exploited in accelerated preimage reconstruction under the condition function.
- These concepts are applied to an in-depth collision analysis of reduced-round versions of the two SHA-3 candidates CubeHash and MD6, and are demonstrated to give by far the best currently known collision attacks on these SHA-3 candidates.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120558 (1).pdf`
- `downloads/59120558 (2).pdf`
- `downloads/59120558 (3).pdf`
- `downloads/59120558.pdf`
