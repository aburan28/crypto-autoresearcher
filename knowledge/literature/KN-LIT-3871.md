---
id: KN-LIT-3871
type: literature
title: "FHEW: Bootstrapping Homomorphic Encryption in less than a second‹"
authors:
  - "Centrum Wiskunde & Informatica"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, mov-fr, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The main bottleneck affecting the efficiency of all known fully homomorphic encryption (FHE) schemes is Gentry’s bootstrapping procedure, which is required to refresh noisy ciphertexts and keep computing on encrypted data. Bootstrapping in the latest implementation of FHE, the HElib library of Halevi and Shoup (Crypto 2014), requires about six minutes.

## Key claims (as reported)
- We present a new method to homomorphically compute simple bit operations, and refresh (bootstrap) the resulting output, which runs on a personal computer in just about half a second.
- We present a detailed technical analysis of the scheme (based on the worst-case hardness of standard lattice problems) and report on the performance of our prototype implementation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560159 (1).pdf`
- `downloads/90560159.pdf`
