---
id: KN-LIT-5841
type: literature
title: "Practical Free-Start Collision Attacks on 76-step"
authors:
  - "Pierre Karpman"
  - "Thomas Peyrin"
  - "Marc Stevens"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, lattice, mov-fr, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we analyze the security of the compression function of SHA-1 against collision attacks, or equivalently free-start collisions on the hash function. While a lot of work has been dedicated to the analysis of SHA-1 in the past decade, this is the first time that free-start collisions have been considered for this function.

## Key claims (as reported)
- We exploit the additional freedom provided by this model by using a new start-from-the-middle approach in combination with improvements on the cryptanalysis tools that have been developed for SHA-1 in the recent years.
- This results in particular in better differential paths than the ones used for hash function collisions so far.
- Overall, our attack requires about 250 evaluations of the compression function in order to compute a one-block free-start collision for a 76-step reduced version, which is so far the highest number of steps reached for a collision on the SHA-1 compression function.
- We have developed an efficient GPU framework for the highly branching code typical of a cryptanalytic collision attack and used it in an optimized implementation of our attack on recent GTX 970 GPUs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160165 (1).pdf`
- `downloads/92160165 (2).pdf`
- `downloads/92160165.pdf`
