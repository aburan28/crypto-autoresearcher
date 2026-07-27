---
id: KN-LIT-4794
type: literature
title: "Low Weight Discrete Logarithm and Subset Sum in 20.65n with Polynomial Memory"
authors:
  - "Andre Esser"
  - "Alexander May∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, dlp, lattice, pollard-rho, provable-security, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose two heuristic polynomial memory collision finding algorithms for the low Hamming weight discrete logarithm problem in any abelian group G. The first one is a direct adaptation of the BeckerCoron-Joux (BCJ) algorithm for subset sum to the discrete logarithm setting.

## Key claims (as reported)
- The second one significantly improves on this adaptation for all possible weights using a more involved application of the representation technique together with some new Markov chain analysis.
- In contrast to other low weight discrete logarithm algorithms, our second algorithm’s 1 time complexity interpolates to Pollard’s |G| 2 bound for general discrete logarithm instances.
- We also introduce a new heuristic subset sum algorithm with polynomial memory that improves on BCJ’s 20.72n time bound for random subset sum instances a1 , . . . , an , t ∈ Z2n .
- Technically, we introduce a novel nested collision finding for subset sum – inspired by the NestedRho algorithm from Crypto ’16 – that recursively produces collisions.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105111 (1).pdf`
- `downloads/12105111.pdf`
