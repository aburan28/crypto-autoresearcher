---
id: KN-LIT-4590
type: literature
title: "Key-Alternating Ciphers in a Provable Setting: Encryption Using a Small Number of Public Permutations?"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper considers—for the first time—the concept of keyalternating ciphers in a provable security setting. Key-alternating ciphers can be seen as a generalization of a construction proposed by Even and Mansour in 1991.

## Key claims (as reported)
- This construction builds a block cipher P X from an n-bit permutation P and two n-bit keys k0 and k1 , setting P Xk0 ,k1 (x) = k1 ⊕ P (x ⊕ k0 ).
- Here we consider a (natural) extension of the EvenMansour construction with t permutations P1 , . . . , Pt and t + 1 keys, k0 , . . . , kt .
- We demonstrate in a formal model that such a cipher is secure in the sense that an attacker needs to make at least 22n/3 queries to the underlying permutations to be able to distinguish the construction from random.
- We argue further that the bound is tight for t = 2 but there is a gap in the bounds for t > 2, which is left as an open and interesting problem.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370046 (1).pdf`
- `downloads/72370046 (2).pdf`
- `downloads/72370046 (3).pdf`
- `downloads/72370046.pdf`
