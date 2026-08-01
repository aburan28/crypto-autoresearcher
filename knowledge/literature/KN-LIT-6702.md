---
id: KN-LIT-6702
type: literature
title: "Slide Reduction, Revisited—Filling the Gaps in SVP Approximation"
authors:
  - "Divesh Aggarwal"
  - "Jianwei Li"
  - "Phong Q. Nguyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, lattice, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show how to generalize Gama and Nguyen’s slide reduction algorithm [STOC ’08] for solving the approximate Shortest Vector Problem over lattices (SVP) to allow for arbitrary block sizes, rather than just block sizes that divide the rank n of the lattice. This leads to significantly better running times for most approximation factors.

## Key claims (as reported)
- We accomplish this by combining slide reduction with the DBKZ algorithm of Micciancio and Walter [Eurocrypt ’16].
- We also show a different algorithm that works when the block size is quite large—at least half the total rank.
- This yields the first non-trivial algorithm for sublinear approximation factors.
- Together with some additional optimizations, these results yield significantly faster provably correct algorithms for δ-approximate SVP for all approximation factors n1/2+ε ≤ δ ≤ nO(1) , which is the regime most relevant for cryptography.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171136 (1).pdf`
- `downloads/12171136.pdf`
