---
id: KN-LIT-2184
type: literature
title: "A Polynomial-Time Algorithm for Solving the Hidden Subset Sum Problem"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, provable-security, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Crypto ’99, Nguyen and Stern described a lattice based algorithm for solving the hidden subset sum problem, a variant of the classical subset sum problem where the n weights are also hidden. While the Nguyen-Stern algorithm works quite well in practice for moderate values of n, we argue that its complexity is actually exponential in n; namely in the final step one must recover a very short basis of a ndimensional lattice, which takes exponential-time in n, as one must apply BKZ reduction with increasingly large block-sizes.

## Key claims (as reported)
- In this paper, we describe a variant of the Nguyen-Stern algorithm that works in polynomial-time.
- The first step is the same orthogonal lattice attack with LLL as in the original algorithm.
- In the second step, instead of applying BKZ, we use a multivariate technique that recovers the short lattice vectors and finally the hidden secrets in polynomial time.
- Our algorithm works quite well in practice, as we can reach n ≃ 250 in a few hours on a single PC.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171041 (1).pdf`
- `downloads/12171041.pdf`
