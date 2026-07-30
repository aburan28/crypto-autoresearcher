---
id: KN-LIT-2472
type: literature
title: "An Efficient and Parallel Gaussian Sampler for Lattices"
authors:
  - "Chris Peikert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At the heart of many recent lattice-based cryptographic schemes is a polynomial-time algorithm that, given a ‘high-quality’ basis, generates a lattice point according to a Gaussian-like distribution. Unlike most other operations in lattice-based cryptography, however, the known algorithm for this task (due to Gentry, Peikert, and Vaikuntanathan; STOC 2008) is rather inefficient, and is inherently sequential.

## Key claims (as reported)
- We present a new Gaussian sampling algorithm for lattices that is efficient and highly parallelizable.
- We also show that in most cryptographic applications, the algorithm’s efficiency comes at almost no cost in asymptotic security.
- At a high level, our algorithm resembles the “perturbation” heuristic proposed as part of NTRUSign (Hoffstein et al., CT-RSA 2003), though the details are quite different.
- To our knowledge, this is the first algorithm and rigorous analysis demonstrating the security of a perturbation-like technique.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230080 (1).pdf`
- `downloads/62230080 (2).pdf`
- `downloads/62230080 (3).pdf`
- `downloads/62230080.pdf`
