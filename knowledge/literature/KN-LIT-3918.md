---
id: KN-LIT-3918
type: literature
title: "FOAM: Searching for Hardware-Optimal SPN Structures and Components with a Fair Comparison"
authors:
  - "Khoongming Khoo"
  - "Thomas Peyrin"
  - "Axel Y. Poschmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we propose a new comparison metric, the figure of adversarial merit (FOAM), which combines the inherent security provided by cryptographic structures and components with their implementation properties. To the best of our knowledge, this is the first such metric proposed to ensure a fairer comparison of cryptographic designs.

## Key claims (as reported)
- We then apply this new metric to meaningful use cases by studying Substitution-Permutation Network permutations that are suited for hardware implementations, and we provide new results on hardwarefriendly cryptographic building blocks.
- For practical reasons, we considered linear and differential attacks and we restricted ourselves to fully serial and round-based implementations.
- We explore several design strategies, from the geometry of the internal state to the size of the S-box, the field size of the diffusion layer or even the irreducible polynomial defining the finite field.
- We finally test all possible strategies to provide designers an exhaustive approach in building hardware-friendly cryptographic primitives (according to area or FOAM metrics), also introducing a model for predicting the hardware performance of round-based or serial-based implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310121 (1).pdf`
- `downloads/87310121 (2).pdf`
- `downloads/87310121 (3).pdf`
- `downloads/87310121.pdf`
