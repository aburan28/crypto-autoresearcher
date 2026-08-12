---
id: KN-LIT-2301
type: literature
title: "Accelerating Homomorphic Evaluation on Reconfigurable Hardware"
authors:
  - "Thomas Pöppelmann"
  - "Michael Naehrig"
  - "Andrew Putnam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Homomorphic encryption allows computation on encrypted data and makes it possible to securely outsource computational tasks to untrusted environments. However, all proposed schemes are quite inefficient and homomorphic evaluation of ciphertexts usually takes several seconds on high-end CPUs, even for evaluating simple functions.

## Key claims (as reported)
- In this work we investigate the potential of FPGAs for speeding up those evaluation operations.
- We propose an architecture to accelerate schemes based on the ring learning with errors (RLWE) problem and specifically implemented the somewhat homomorphic encryption scheme YASHE, which was proposed by Bos, Lauter, Loftus, and Naehrig in 2013.
- Due to the large size of ciphertexts and evaluation keys, on-chip storage of all data is not possible and external memory is required.
- For efficient utilization of the external memory we propose an efficient double-buffered memory access scheme and a polynomial multiplier based on the number theoretic transform (NTT).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930139 (1).pdf`
- `downloads/92930139.pdf`
