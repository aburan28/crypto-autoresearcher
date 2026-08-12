---
id: KN-LIT-2661
type: literature
title: "Batch Bootstrapping II: Bootstrapping in Polynomial Modulus Only Requires Õ(1) FHE Multiplications in Amortization"
authors:
  - "Feng-Hao Liu"
  - "Han Wang (Corresponding Author)"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work continues the exploration of the batch framework proposed in Batch Bootstrapping I (Liu and Wang, Eurocrypt 2023). By further designing novel batch homomorphic algorithms based on the batch framework, this work shows how to bootstrap λ LWE input ciphertexts within a polynomial modulus, using Õ(λ) FHE multiplications.

## Key claims (as reported)
- This implies an amortized complexity Õ(1) FHE multiplications per input ciphertext, significantly improving our first work (whose amortized complexity is Õ(λ0.75 )) and the theoretical state of the art MS18 (Micciancio and Sorrell, ICALP 2018), whose amortized complexity is O(31/ε · λε ), for any arbitrary constant ε.
- We believe that all our new homomorphic algorithms might be useful in general applications, and thus can be of independent interests.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004257 (1).pdf`
- `downloads/14004257.pdf`
