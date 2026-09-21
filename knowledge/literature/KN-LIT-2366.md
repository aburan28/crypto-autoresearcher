---
id: KN-LIT-2366
type: literature
title: "Advanced Lattice Sieving on GPUs, with Tensor Cores"
authors:
  - "The Netherlands"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we study GPU implementations of various state-of-the-art sieving algorithms for lattices (Becker-Gama-Joux 2015, Becker-Ducas-Gama-Laarhoven 2016, Herold-Kirshanova 2017) inside the General Sieve Kernel (G6K, Albrecht et al. In particular, we extensively exploit the recently introduced Tensor Cores – originally designed for raytracing and machine learning – and demonstrate their fitness for the cryptanalytic task at hand.

## Key claims (as reported)
- We also propose a new dual-hash technique for efficient detection of ‘lift-worthy’ pairs to accelerate a key ingredient of G6K: finding short lifted vectors.
- We obtain new computational records, reaching dimension 180 for the SVP Darmstadt Challenge improving upon the previous record for dimension 155.
- This computation ran for 51.6 days on a server with 4 NVIDIA Turing GPUs and 1.5TB of RAM.
- This corresponds to a gain of about two orders of magnitude over previous records both in terms of wall-clock time and of energy efficiency.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960219 (1).pdf`
- `downloads/126960219.pdf`
