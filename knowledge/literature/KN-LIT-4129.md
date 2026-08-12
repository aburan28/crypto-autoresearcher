---
id: KN-LIT-4129
type: literature
title: "Graph-Theoretic Algorithms for the “Isomorphism of Polynomials” Problem"
authors:
  - "Charles Bouillaguet@Univ-Lille"
  - "Pierre-Alain Fouque"
  - "Amandine Véber"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give three new algorithms to solve the “isomorphism of polynomial” problem, which was underlying the hardness of recovering the secret-key in some multivariate trapdoor one-way functions. In this problem, the adversary is given two quadratic functions, with the promise that they are equal up to linear changes of coordinates.

## Key claims (as reported)
- Her objective is to compute these changes of coordinates, a task which is known to be harder than Graph-Isomorphism.
- Our new algorithm build on previous work in a novel way.
- Exploiting the birthday paradox, we break instances of the problem in time q 2n/3 (rigorously) and q n/2 (heuristically), where q n is the time needed to invert the quadratic trapdoor function by exhaustive search.
- These results are obtained by turning the algebraic problem into a combinatorial one, namely that of recovering partial information on an isomorphism between two exponentially large graphs.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/78810209 (1).pdf`
- `downloads/78810209 (2).pdf`
- `downloads/78810209 (3).pdf`
- `downloads/78810209.pdf`
