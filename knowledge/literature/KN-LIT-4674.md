---
id: KN-LIT-4674
type: literature
title: "Leakage Resilient Fully Homomorphic Encryption"
authors:
  - "Alexandra Berkoff"
  - "Feng-Hao Liu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mov-fr, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the first leakage resilient variants of fully homomorphic encryption (FHE) schemes. Our leakage model is bounded adaptive leakage resilience.

## Key claims (as reported)
- We first construct a leakage-resilient leveled FHE scheme, meaning the scheme is homomorphic for all circuits of depth less than some pre-established maximum set at key generation.
- We do so by applying ideas from recent works analyzing the leakage resilience of public key encryption schemes based on the decision learning with errors (DLWE ) assumption to the Gentry, Sahai and Waters ([?]) leveled FHE scheme.
- We then move beyond simply leveled FHE, removing the need for an a priori maximum circuit depth, by presenting a novel way to combine schemes.
- We show that by combining leakage resilient leveled FHE with multi-key FHE, it is possible to create a leakage resilient scheme capable of homomorphically evaluating circuits of arbitrary depth, with a bounded number of distinct input ciphertexts.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83490158 (1).pdf`
- `downloads/83490158 (2).pdf`
- `downloads/83490158 (3).pdf`
- `downloads/83490158.pdf`
