---
id: KN-LIT-4528
type: literature
title: "Integral Matrix Gram Root and Lattice Gaussian Sampling without Floats"
authors:
  - "Centrum Wiskunde en Informatica"
  - "The Netherlands"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, lattice, pqc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many advanced lattice based cryptosystems require to sample lattice points from Gaussian distributions. One challenge for this task is that all current algorithms resort to floating-point arithmetic (FPA) at some point, which has numerous drawbacks in practice: it requires numerical stability analysis, extra storage for high-precision, lazy/backtracking techniques for efficiency, and may suffer from weak determinism which can completely break certain schemes.

## Key claims (as reported)
- In this paper, we give techniques to implement Gaussian sampling over general lattices without using FPA.
- To this end, we revisit the approach of Peikert, using perturbation sampling.
- Peikert’s approach uses continuous Gaussian sampling and some decomposition Σ = AAt of the target covariance matrix Σ.
- The suggested decomposition, e.g. the Cholesky decomposition, gives rise to a square matrix A with real (not integer) entries.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105173 (1).pdf`
- `downloads/12105173.pdf`
