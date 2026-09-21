---
id: KN-LIT-2772
type: literature
title: "Bootstrapping fully homomorphic encryption over the integers in less than one second"
authors:
  - "Hilder Vitor Lima Pereira"
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
One can bootstrap LWE-based fully homomorphic encryption (FHE) schemes in less than one second, but bootstrapping AGCDbased FHE schemes, also known as FHE over the integers, is still very slow. In this work we propose a fast bootstrapping method for FHE over the integers, closing thus this gap between these two types of schemes.

## Key claims (as reported)
- We use a variant of the AGCD problem to construct a new GSW-like scheme that can natively encrypt polynomials, then, we show how the single-gate bootstrapping method proposed by Ducas and Micciancio (EUROCRYPT 2015) can be adapted to FHE over the integers using our scheme, and we implement a bootstrapping that, using around 400 MB of key material, runs in less than one second in a common personal computer.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110110 (1).pdf`
- `downloads/127110110.pdf`
