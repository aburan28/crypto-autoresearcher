---
id: KN-LIT-6943
type: literature
title: "The Additive Differential Probability of ARX"
authors:
  - "Vesselin Velichkov⋆⋆"
  - "Nicky Mouha⋆ ⋆ ⋆"
  - "Christophe De Cannière"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We analyze adpARX , the probability with which additive differences propagate through the following sequence of operations: modular addition, bit rotation and XOR (ARX). We propose an algorithm to evaluate adpARX with a linear time complexity in the word size.

## Key claims (as reported)
- This algorithm is based on the recently proposed concept of S-functions.
- Because of the bit rotation operation, it was necessary to extend the S-functions framework.
- We show that adpARX can differ significantly from the multiplication of the differential probability of each component.
- To the best of our knowledge, this paper is the first to propose an efficient algorithm to calculate adpARX .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330350 (1).pdf`
- `downloads/67330350 (2).pdf`
- `downloads/67330350 (3).pdf`
- `downloads/67330350.pdf`
