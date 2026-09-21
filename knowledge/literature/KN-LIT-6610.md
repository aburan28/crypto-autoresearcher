---
id: KN-LIT-6610
type: literature
title: "Shuffling Against Side-Channel Attacks: a Comprehensive Study with Cautionary Note Nicolas Veyrat-Charvillon, Marcel Medwed"
authors:
  - "B- Louvain-la-Neuve"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Together with masking, shuffling is one of the most frequently considered solutions to improve the security of small embedded devices against side-channel attacks. In this paper, we provide a comprehensive study of this countermeasure, including improved implementations and a careful information theoretic and security analysis of its different variants.

## Key claims (as reported)
- Our analyses lead to important conclusions as they moderate the strong security improvements claimed in previous works.
- They suggest that simplified versions of shuffling (e.g. using random start indexes) can be significantly weaker than their counterpart using full permutations.
- We further show with an experimental case study that such simplified versions can be as easy to attack as unprotected implementations.
- We finally exhibit the existence of “indirect leakages” in shuffled implementations that can be exploited due to the different leakage models of the different resources used in cryptographic implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580728 (1).pdf`
- `downloads/76580728 (2).pdf`
- `downloads/76580728 (3).pdf`
- `downloads/76580728.pdf`
