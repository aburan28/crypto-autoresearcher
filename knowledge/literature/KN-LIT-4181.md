---
id: KN-LIT-4181
type: literature
title: "HERMES: Efficient Ring Packing using MLWE"
authors:
  - "Application to Transciphering"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, implementation, lattice, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Most of the current fully homomorphic encryption (FHE) schemes are based on either the learning-with-errors (LWE) problem or on its ring variant (RLWE) for storing plaintexts. During the homomorphic computation of FHE schemes, RLWE formats provide high throughput when considering several messages, and LWE formats provide a low latency when there are only a few messages.

## Key claims (as reported)
- Efficient conversion can bridge the advantages of each format.
- However, converting LWE formats into RLWE format, which is called ring packing, has been a challenging problem.
- We propose an efficient solution for ring packing for FHE.
- The main improvement of this work is twofold.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850241 (1).pdf`
- `downloads/140850241.pdf`
