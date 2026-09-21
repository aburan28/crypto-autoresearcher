---
id: KN-LIT-5164
type: literature
title: "Non-Adaptive Universal One-Way Hash Functions from Arbitrary One-Way Functions"
authors:
  - "Xinyu Mao"
  - "Noam Mazor"
  - "Jiapeng Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we give the first non-adaptive construction of universal one-way hash functions (UOWHFs) from arbitrary one-way functions. Our construction uses O(n9 ) calls to the one-way function, has a key of length O(n10 ), and can be implemented in NC1 assuming the underlying one-way function is in NC1.

## Key claims (as reported)
- Prior to this work, the best UOWHF construction used O(n13 ) adaptive calls and a key of size O(n5 ) (Haitner, Holenstein, Reingold, Vadhan and Wee [Eurocrypt ’10]).
- By the result of Applebaum, Ishai and Kushilevitz [FOCS ’04], the above implies the existence of UOWHFs in NC0, given the existence of one-way functions in NC1.
- We also show that the PRG construction of Haitner, Reingold and Vadhan (HRV, [STOC ’10]), with small modifications, yields a relaxed notion of UOWHFs , which is a function family which can be (inefficiently) converted to UOWHF by changing the functions on a negligible fraction of the inputs.
- In order to analyze this construction, we introduce the notion of next-bit unreachable entropy, which replaces the next-bit pseudoentropy notion used by HRV.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004030 (1).pdf`
- `downloads/14004030.pdf`
