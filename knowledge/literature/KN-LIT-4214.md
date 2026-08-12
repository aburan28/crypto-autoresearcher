---
id: KN-LIT-4214
type: literature
title: "Higher-order differential properties of Keccak and Luffa ?"
authors:
  - "Christina Boura"
  - "Anne Canteaut"
  - "Christophe De Cannière"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we identify higher-order differential and zerosum properties in the full Keccak-f permutation, in the Luffa v1 hash function and in components of the Luffa v2 algorithm. These structural properties rely on a new bound on the degree of iterated permutations with a nonlinear layer composed of parallel applications of a number of balanced Sboxes.

## Key claims (as reported)
- These techniques yield zero-sum partitions of size 21575 for the full Keccak-f permutation and several observations on the Luffa hash family.
- We first show that Luffa v1 applied to one-block messages is a function of 255 variables with degree at most 251.
- This observation leads to the construction of a higher-order differential distinguisher for the full Luffa v1 hash function, similar to the one presented by Watanabe et al. on a reduced version.
- We show that similar techniques can be used to find all-zero higher-order differentials in the Luffa v2 compression function, but the additional blank round destroys this property in the hash function.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330258 (1).pdf`
- `downloads/67330258 (2).pdf`
- `downloads/67330258 (3).pdf`
- `downloads/67330258.pdf`
