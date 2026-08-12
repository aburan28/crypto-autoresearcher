---
id: KN-LIT-3841
type: literature
title: "Faster Gaussian Lattice Sampling using Lazy Floating-Point Arithmetic"
authors:
  - "Dept. Informatique"
  - "rue d’Ulm"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, lattice, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many lattice cryptographic primitives require an efficient algorithm to sample lattice points according to some Gaussian distribution. All algorithms known for this task require long-integer arithmetic at some point, which may be problematic in practice.

## Key claims (as reported)
- We study how much lattice sampling can be sped up using floating-point arithmetic.
- First, we show that a direct floating-point implementation of these algorithms does not give any asymptotic speedup: the floating-point precision needs to be greater than the security parameter, leading to an overall complexity Õ(n3 ) where n is the lattice dimension.
- However, we introduce a laziness technique that can significantly speed up these algorithms.
- Namely, in certain cases such as NTRUSign lattices, laziness can decrease the complexity to Õ(n2 ) or even Õ(n).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/76580410 (1).pdf`
- `downloads/76580410 (2).pdf`
- `downloads/76580410 (3).pdf`
- `downloads/76580410.pdf`
