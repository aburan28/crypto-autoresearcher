---
id: KN-LIT-4269
type: literature
title: "How to Compress Encrypted Data"
authors:
  - "Nils Fleischhacker"
  - "Kasper Green"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the task of obliviously compressing a vector comprised of n ciphertexts of size ξ bits each, where at most t of the corresponding plaintexts are non-zero. This problem commonly features in applications involving encrypted outsourced storages, such as searchable encryption or oblivious message retrieval.

## Key claims (as reported)
- We present two new algorithms with provable worst-case guarantees, solving this problem by using only homomorphic additions and multiplications by constants.
- Both of our new constructions improve upon the state of the art asymptotically and concretely.
- Our first construction, based on sparse polynomials, is perfectly correct and the first to achieve an asymptotically optimal compression rate by compressing the input vector into O(tξ) bits.
- Compression can be performed homomorphically by performing O(n log n) homomorphic additions and multiplications by constants.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004415 (1).pdf`
- `downloads/14004415.pdf`
