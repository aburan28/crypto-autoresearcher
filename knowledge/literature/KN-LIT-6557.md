---
id: KN-LIT-6557
type: literature
title: "Separating IND-CPA and Circular Security for Unbounded Length Key Cycles"
authors:
  - "Rishab Goyal"
  - "Venkata Koppula"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A public key encryption scheme is said to be n-circular secure if no PPT adversary can distinguish between encryptions of an n length key cycle and n encryptions of zero. One interesting question is whether circular security comes for free from IND-CPA security.

## Key claims (as reported)
- Recent works have addressed this question, showing that for all integers n, there exists an IND-CPA scheme that is not n-circular secure.
- However, this leaves open the possibility that for every IND-CPA cryptosystem, there exists a cycle length l, dependent on the cryptosystem (and the security parameter) such that the scheme is l-circular secure.
- If this is true, then this would directly lead to many applications, in particular, it would give us a fully homomorphic encryption scheme via Gentry’s bootstrapping.
- In this work, we show that is not true.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101740222 (1).pdf`
- `downloads/101740222 (2).pdf`
- `downloads/101740222 (3).pdf`
- `downloads/101740222 (4).pdf`
- `downloads/101740222.pdf`
