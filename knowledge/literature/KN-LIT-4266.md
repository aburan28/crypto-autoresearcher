---
id: KN-LIT-4266
type: literature
title: "How to Build Pseudorandom Functions From Public Random Permutations"
authors:
  - "Yu Long Chen"
  - "Eran Lambooij"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, protocol, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Pseudorandom functions are traditionally built upon block ciphers, but with the trend of permutation based cryptography, it is a natural question to investigate the design of pseudorandom functions from random permutations. We present a generic study of how to build beyond birthday bound secure pseudorandom functions from public random permutations.

## Key claims (as reported)
- We first show that a pseudorandom function based on a single permutation call cannot be secure beyond the 2n/2 birthday bound, where n is the state size of the function.
- We next consider the Sum of Even-Mansour (SoEM) construction, that instantiates the sum of permutations with the Even-Mansour construction.
- We prove that SoEM achieves tight 2n/3-bit security if it is constructed from two independent permutations and two randomly drawn keys.
- We also demonstrate a birthday bound attack if either the permutations or the keys are identical.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940450 (1).pdf`
- `downloads/116940450.pdf`
