---
id: KN-LIT-3762
type: literature
title: "Efficient Reconstruction of RC4 Keys from Internal States"
authors:
  - "Eli Biham"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, protocol, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present an efficient algorithm for the retrieval of the RC4 secret key, given an internal state. This algorithm is several orders of magnitude faster than previously published algorithms.

## Key claims (as reported)
- In the case of a 40-bit key, it takes only about 0.02 seconds to retrieve the key, with success probability of 86.4%.
- Even if the algorithm cannot retrieve the entire key, it can retrieve partial information about the key.
- The key can also be retrieved if some of the bytes of the initial permutation are incorrect or missing.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/50860272 (1).pdf`
- `downloads/50860272 (2).pdf`
- `downloads/50860272 (3).pdf`
- `downloads/50860272.pdf`
