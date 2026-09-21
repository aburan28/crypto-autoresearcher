---
id: KN-LIT-4537
type: literature
title: "Internal Differential Boomerangs: Practical Analysis of the Round-Reduced Keccak-f Permutation"
authors:
  - "Jérémy Jean"
  - "Ivica Nikolić"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce internal differential boomerang distinguisher as a combination of internal differentials and classical boomerang distinguishers. The new boomerangs can be successful against cryptographic primitives having high-probability round-reduced internal differential characteristics.

## Key claims (as reported)
- The internal differential technique, which follow the evolution of differences between parts of the state, is particularly meaningful for highly symmetric functions like the inner permutation Keccak-f of the hash functions defined in the future SHA-3 standard.
- We find internal differential and standard characteristics for three to four rounds of Keccak-f , and with the use of the new technique, enhanced with a strong message modification, show practical distinguishers for this permutation.
- Namely, we need 212 queries to distinguish 7 rounds of the permutation starting from the first round, and approximately 218 queries to distinguish 8 rounds starting from the fourth round.
- Due to the exceptionally low complexities, all of our results have been completely verified with a computer implementation of the analysis.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400113 (1).pdf`
- `downloads/85400113.pdf`
