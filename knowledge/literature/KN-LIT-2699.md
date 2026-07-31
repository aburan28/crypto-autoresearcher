---
id: KN-LIT-2699
type: literature
title: "Beyond-Birthday-Bound Security for Tweakable Even-Mansour Ciphers with Linear Tweak and Key Mixing"
authors:
  - "Benoît Cogliati"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The iterated Even-Mansour construction defines a block cipher from a tuple of public n-bit permutations (P1 , . . . , Pr ) by alternatively xoring some n-bit round key ki , i = 0, . . . , r, and applying permutation Pi to the state. The tweakable Even-Mansour construction generalizes the conventional Even-Mansour construction by replacing the n-bit round keys by n-bit strings derived from a master key and a tweak, thereby defining a tweakable block cipher.

## Key claims (as reported)
- Constructions of this type have been previously analyzed, but they were either secure only up to the birthday bound, or they used a nonlinear mixing function of the key and the tweak (typically, multiplication of the key and the tweak seen as elements of some finite field) which might be costly to implement.
- In this paper, we tackle the question of whether it is possible to achieve beyond-birthday-bound security for such a construction by using only linear operations for mixing the key and the tweak into the state.
- We answer positively, describing a 4-round construction with a 2n-bit master key and an n-bit tweak which is provably secure in the Random Permutation Model up to roughly 22n/3 adversarial queries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520211 (1).pdf`
- `downloads/94520211.pdf`
