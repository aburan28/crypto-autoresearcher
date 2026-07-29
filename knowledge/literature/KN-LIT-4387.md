---
id: KN-LIT-4387
type: literature
title: "Improved Collision Search for SHA-0"
authors:
  - "Jun Yajima"
  - "Noboru Kunihiro"
  - "Kazuo Ohta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO2005, Xiaoyun Wang, Hongbo Yu and Yiqun Lisa Yin proposed a collision attack on SHA-0 that could generate a collision with complexity 239 SHA-0 hash operations. Although the method of Wang et al. can find messages that satisfy the sufficient conditions in steps 1 to 20 by using message modification, it makes no mention of the message modifications needed to yield satisfaction of the sufficient conditions in steps 21 and onwards.

## Key claims (as reported)
- In this paper, first, we give sufficient conditions for the steps from step 21, and propose submarine modification as the message modification technique that will ensure satisfaction of the sufficient conditions from steps 21 to 24.
- Submarine modification is an extension of the multi-message modification used in collision attacks on the MD-family.
- Next, we point out that the sufficient conditions given by Wang et al. are not enough to generate a collision with high probability; we rectify this shortfall by introducing two new sufficient conditions.
- The combination of our newly found sufficient conditions and submarine modification allows us to generate a collision with complexity 236 SHA-0 hash operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840021 (1).pdf`
- `downloads/42840021 (2).pdf`
- `downloads/42840021 (3).pdf`
- `downloads/42840021.pdf`
