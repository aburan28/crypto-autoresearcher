---
id: KN-LIT-4159
type: literature
title: "Hardness Preserving Constructions of Pseudorandom Functions"
authors:
  - "Abhishek Jain⋆"
  - "Krzysztof Pietrzak⋆⋆"
  - "Aris Tentes⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show a hardness-preserving construction of a PRF from any length doubling PRG which improves upon known constructions whenever we can put a non-trivial upper bound q on the number of queries to the PRF. Our construction requires only O(log q) invocations to the underlying PRG with each query.

## Key claims (as reported)
- In comparison, the number of invocations by the best previous hardness-preserving construction (GGM using Levin’s trick) is logarithmic in the hardness of the PRG.
- For example, starting from an exponentially secure PRG {0, 1}n 7→ {0, 1}2n , we get a PRF which is exponentially secure if queried at most √ q = exp( n) times and where each invocation of the PRF requires √ Θ( n) queries to the underlying PRG.
- This is much less than the Θ(n) required by known constructions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940204 (1).pdf`
- `downloads/71940204 (2).pdf`
- `downloads/71940204 (3).pdf`
- `downloads/71940204.pdf`
