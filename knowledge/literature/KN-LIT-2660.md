---
id: KN-LIT-2660
type: literature
title: "Batch Bootstrapping I: A New Framework for SIMD Bootstrapping in Polynomial Modulus"
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
tags: [fhe, implementation, lattice, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this series of work, we aim at improving the bootstrapping paradigm for fully homomorphic encryption (FHE). Our main goal is to show that the amortized cost of bootstrapping within a polynomial modulus only requires Õ(1) FHE multiplications.

## Key claims (as reported)
- To achieve this, we develop substantial algebraic techniques in two papers.
- Particularly, the first one (this work) proposes a new mathematical framework for batch homomorphic computation that is compatible with the existing bootstrapping methods of AP14/FHEW/TFHE.
- To show that our overall method requires only a polynomial modulus, we develop a critical algebraic analysis over noise growth, which might be of independent interest.
- Overall, the framework yields an amortized complexity Õ(λ0.75 ) FHE multiplications, where λ is the security parameter.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004255 (1).pdf`
- `downloads/14004255.pdf`
