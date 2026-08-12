---
id: KN-LIT-3963
type: literature
title: "From Non-Adaptive to Adaptive Pseudorandom Functions"
authors:
  - "Itay Berman"
  - "Iftach Haitner⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Unlike the standard notion of pseudorandom functions (PRF), a non-adaptive PRF is only required to be indistinguishable from random in the eyes of a non-adaptive distinguisher (i.e., one that prepares its oracle calls in advance). A recent line of research has studied the possibility of a direct construction of adaptive PRFs from non-adaptive ones, where direct means that the constructed adaptive PRF uses only few (ideally, constant number of) calls to the underlying non-adaptive PRF.

## Key claims (as reported)
- Unfortunately, this study has only yielded negative results, showing that “natural” such constructions are unlikely to exist (e.g., Myers [EUROCRYPT ’04], Pietrzak [CRYPTO ’05, EUROCRYPT ’06]).
- We give an affirmative answer to the above question, presenting a direct construction of adaptive PRFs from non-adaptive ones.
- Our construction is extremely simple, a composition of the non-adaptive PRF with an appropriate pairwise independent hash function.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940130 (1).pdf`
- `downloads/71940130 (2).pdf`
- `downloads/71940130 (3).pdf`
- `downloads/71940130.pdf`
