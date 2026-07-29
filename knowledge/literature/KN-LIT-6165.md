---
id: KN-LIT-6165
type: literature
title: "Rebound Attack on Reduced-Round Versions of JH"
authors:
  - "Vincent Rijmen"
  - "Deniz Toz"
  - "Kerem Varıcı"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
JH, designed by Wu, is one of the 14 second-round candidates in the NIST Hash Competition. This paper presents the first analysis results of JH by using rebound attack.

## Key claims (as reported)
- We first investigate a variant of the JH hash function family for d = 4 and describe how the attack works.
- Then, we apply the attack for d = 8, which is the version submitted to the competition.
- As a result, we obtain a semi-free-start collision for 16 rounds (out of 35.5) of JH for all hash sizes with 2179.24 compression function calls.
- We then extend our attack to 19 (and 22) rounds and present a 1008-bit (and 896-bit) semi-free-start near-collision on the JH compression function with 2156.77 (2156.56 ) compression function calls, 2152.28 memory access and 2143.70 -bytes of memory.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470292 (1).pdf`
- `downloads/61470292 (2).pdf`
- `downloads/61470292 (3).pdf`
- `downloads/61470292.pdf`
