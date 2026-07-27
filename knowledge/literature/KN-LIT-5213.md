---
id: KN-LIT-5213
type: literature
title: "Non-Malleable Codes from Two-Source Extractors?"
authors:
  - "Stefan Dziembowski"
  - "Tomasz Kazana"
  - "Maciej Obremski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct an efficient information-theoretically non-malleable code in the split-state model for one-bit messages. Non-malleable codes were introduced recently by Dziembowski, Pietrzak and Wichs (ICS 2010), as a general tool for storing messages securely on hardware that can be subject to tampering attacks.

## Key claims (as reported)
- Informally, a code (Enc : M → L × R, Dec : L × R → M) is non-malleable in the split-state model if any adversary, by manipulating independently L and R (where (L, R) is an encoding of some message M ), cannot obtain an encoding of a message M 0 that is not equal to M but is “related” M in some way.
- Until now it was unknown how to construct an information-theoretically secure code with such a property, even for M = {0, 1}.
- Our construction solves this problem.
- Additionally, it is leakage-resilient, and the amount of leakage that we can tolerate can be an arbitrary fraction ξ < 1/4 of the length of the codeword.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420193 (1).pdf`
- `downloads/80420193 (2).pdf`
- `downloads/80420193 (3).pdf`
- `downloads/80420193.pdf`
