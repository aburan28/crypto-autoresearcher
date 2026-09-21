---
id: KN-LIT-6532
type: literature
title: "Security-Amplifying Combiners for Collision-Resistant Hash Functions"
authors:
  - "Marc Fischlin"
  - "Anja Lehmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The classical combiner CombH class (M ) = H0 (M )||H1 (M ) for hash functions H0 , H1 provides collision-resistance as long as at least one of the two underlying hash functions is secure. This statement is complemented by the multi-collision attack of Joux (Crypto 2004) for iterated hash functions H0 , H1 with n-bit outputs.

## Key claims (as reported)
- He shows that one can break the classical combiner in n2 · T0 + T1 steps if one can find collisions for H0 and H1 in time T0 and T1 , respectively.
- Here we address the question if there are security-amplifying combiners where the security of the building blocks increases the security of the combined hash function, thus beating the bound of Joux.
- We discuss that one can indeed have such combiners and, somewhat surprisingly in light of results of Nandi and Stinson (ePrint 2004) and of Hoch and Shamir (FSE 2006), our solution is essentially as efficient as the classical combiner.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220224 (1).pdf`
- `downloads/46220224 (2).pdf`
- `downloads/46220224 (3).pdf`
- `downloads/46220224.pdf`
