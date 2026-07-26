---
id: KN-LIT-2494
type: literature
title: "An Improved Affine Equivalence Algorithm for Random Permutations"
authors:
  - "Itai Dinur"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we study the affine equivalence problem, where given two functions F , G : {0, 1}n → {0, 1}n , the goal is to determine whether there exist invertible affine transformations A1 , A2 over GF (2)n such that G = A2 ◦F ◦A1 . Algorithms for this problem have several wellknown applications in the design and analysis of Sboxes, cryptanalysis of white-box ciphers and breaking a generalized Even-Mansour scheme.

## Key claims (as reported)
- We describe a new algorithm for the affine equivalence problem and focus on the variant where F , G are permutations over n-bit words, as it has the widest applicability.
- The complexity of our algorithm is about n3 2n bit operations with very high probability whenever F (or G) is a random permutation.
- This improves upon the best known algorithms for this problem (published by Biryukov et al. at EUROCRYPT 2003), where the first algorithm has time complexity of n3 22n and the second has time complexity of about n3 23n/2 and roughly the same memory complexity.
- Our algorithm is based on a new structure (called a rank table) which is used to analyze particular algebraic properties of a function that remain invariant under invertible affine transformations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822112 (1).pdf`
- `downloads/10822112.pdf`
