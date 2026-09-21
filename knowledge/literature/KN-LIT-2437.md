---
id: KN-LIT-2437
type: literature
title: "Amortized bootstrapping revisited: Simpler, asymptotically-faster, implemented"
authors:
  - "Antonio Guimarães"
  - "Hilder V. L. Pereira"
  - "Barry van Leeuwen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Micciancio and Sorrel (ICALP 2018) proposed a bootstrapping algorithm that can refresh many messages at once with sublinearly many homomorphic operations per message. However, despite the attractive asymptotic cost, it is unclear if their algorithm could ever be practical, which reduces the impact of their results.

## Key claims (as reported)
- In this work, we follow their general framework, but propose an amortized bootstrapping procedure that is conceptually simpler and asymptotically cheaper.
- We reduce the number of homomorphic multiplications per refreshed message from O(3ρ · n1/ρ · log n) to O(ρ · n1/ρ ), and the noise overhead from e 2+3·ρ ) to O(n e 1+ρ ), where n is the security level and ρ ≥ 1 is a free O(n parameter.
- We also make it more general, by handling non-binary messages and applying programmable bootstrapping.
- To obtain a concrete instantiation of our bootstrapping algorithm, we describe a double-CRT (aka RNS) version of the GSW scheme, including a new operation, called shrinking, used to speed-up homomorphic operations by reducing the dimension and ciphertext modulus of the ciphertexts.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438282 (1).pdf`
- `downloads/14438282.pdf`
