---
id: KN-LIT-7069
type: literature
title: "The Security of Many-Round Luby-Rackoff"
authors:
  - "Pseudo-Random Permutations"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Luby and Rackoff showed how to construct a (super-)pseudorandom permutation {0, 1}2n → {0, 1}2n from some number r of pseudorandom functions {0, 1}n → {0, 1}n . Their construction, motivated by DES, consists of a cascade of r Feistel permutations.

## Key claims (as reported)
- A Feistel permutation 1for a pseudo-random function f is defined as (L, R) → (R, L ⊕ f (R)), where L and R are the left and right part of the input and ⊕ denotes bitwise XOR or, in this paper, any other group operation on {0, 1}n .
- The only non-trivial step of the security proof consists of proving that the cascade of r Feistel permutations with independent uniform r random functions {0, 1}n → {0, 1}n , denoted Ψ2n , is indistinguishable 2n from a uniform random permutation {0, 1} → {0, 1}2n by any computationally unbounded adaptive distinguisher making at most O(2cn ) combined chosen plaintext/ciphertext queries for any c < α, where α is a security parameter.
- Luby and Rackoff proved α = 1/2 for r = 4.
- A natural problem, proposed by Pieprzyk is to improve on α for larger r.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560545 (1).pdf`
- `downloads/26560545 (2).pdf`
- `downloads/26560545.pdf`
