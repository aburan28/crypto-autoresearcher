---
id: KN-LIT-3036
type: literature
title: "Compression from Collisions, or why CRHF Combiners have a Long Output Krzysztof Pietrzak"
authors:
  - "CWI Amsterdam"
  - "The Netherlands"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A black-box combiner for collision resistant hash functions (CRHF) is a construction which given black-box access to two hash functions is collision resistant if at least one of the components is collision resistant. In this paper we prove a lower bound on the output length of black-box combiners for CRHFs.

## Key claims (as reported)
- The bound we prove is basically tight as it is achieved by a recent construction of Canetti et al [Crypto’07].
- The best previously known lower bounds only ruled out a very restricted class of combiners having a very strong security reduction: the reduction was required to output collisions for both underlying candidate hash-functions given a single collision for the combiner (Canetti et al [Crypto’07] building on Boneh and Boyen [Crypto’06] and Pietrzak [Eurocrypt’07]).
- Our proof uses a lemma similar to the elegant “reconstruction lemma” of Gennaro and Trevisan [FOCS’00], which states that any function which is not one-way is compressible (and thus uniformly random function must be one-way).
- In a similar vein we show that a function which is not collision resistant is compressible.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51570413 (1).pdf`
- `downloads/51570413 (2).pdf`
- `downloads/51570413 (3).pdf`
- `downloads/51570413.pdf`
