---
id: KN-LIT-4902
type: literature
title: "Merkle Tree Traversal in Log Space and Time"
authors:
  - "Michael Szydlo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a technique for Merkle tree traversal which requires only logarithmic space and time. For a tree with N leaves, our algorithm computes sequential tree leaves and authentication path data in time 2 log2 (N ) and space less than 3 log2 (N ), where the units of computation are hash function evaluations or leaf value computations, and the units of space are the number of node values stored.

## Key claims (as reported)
- This result is an asymptotic improvement over all other previous results (for example, measuring cost = space ∗ time).
- We also prove that the complexity of our algorithm is optimal: There can exist no Merkle tree traversal algorithm which consumes both less than O(log 2 (N )) space and less than O(log2 (N )) time.
- Our algorithm is especially of practical interest when space efficiency is required.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/szydlo-loglog (1).pdf`
- `downloads/szydlo-loglog (2).pdf`
- `downloads/szydlo-loglog.pdf`
