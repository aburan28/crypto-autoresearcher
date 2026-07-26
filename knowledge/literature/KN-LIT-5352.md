---
id: KN-LIT-5352
type: literature
title: "On Hardness Amplification of One-Way Functions"
authors:
  - "Henry Lin"
  - "Luca Trevisan"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We continue the study of the efficiency of black-box reductions in cryptography. We focus on the question of constructing strong one-way functions (respectively, permutations) from weak one-way functions (respectively, permutations).

## Key claims (as reported)
- To make our impossibility results stronger, we focus on the weakest type of constructions: those that start from a weak one-way permutation and define a strong one-way function.
- We show that for every “fully black-box” construction of a 2(n)-secure function based on a (1 − δ(n))-secure permutation, if q(n) is the number of oracle queries used in the construction and `(n) is the input length of the new function, then we have q ≥ Ω( 1δ · log 12 ) and ` ≥ n + Ω(log 1/2) − O(log q).
- This result is proved by showing that fully black-box reductions of strong to weak one-way functions imply the existence of “hitters” and then by applying known lower bounds for hitters.
- We also show a sort of reverse connection, and we revisit the construction of Goldreich et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_037 (1).pdf`
- `downloads/3378_037 (2).pdf`
- `downloads/3378_037 (3).pdf`
- `downloads/3378_037.pdf`
