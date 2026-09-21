---
id: KN-LIT-5714
type: literature
title: "Parallel Gauss Sieve Algorithm: Solving the SVP Challenge over a 128-Dimensional Ideal Lattice"
authors:
  - "Yutaka Miyake"
  - "Tsuyoshi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we report that we have solved the SVP Challenge over a 128-dimensional lattice in Ideal Lattice Challenge from TU Darmstadt, which is currently the highest dimension in the challenge that has ever been solved. The security of lattice-based cryptography is based on the hardness of solving the shortest vector problem (SVP) in lattices.

## Key claims (as reported)
- In 2010, Micciancio and Voulgaris proposed a Gauss Sieve algorithm for heuristically solving the SVP using a list L of Gauss-reduced vectors.
- Milde and Schneider proposed a parallel implementation method for the Gauss Sieve algorithm.
- However, the efficiency of the more than 10 threads in their implementation decreased due to the large number of non-Gauss-reduced vectors appearing in the distributed list of each thread.
- In this paper, we propose a more practical parallelized Gauss Sieve algorithm.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830167 (1).pdf`
- `downloads/83830167 (2).pdf`
- `downloads/83830167 (3).pdf`
- `downloads/83830167 (4).pdf`
- `downloads/83830167 (5).pdf`
- `downloads/83830167.pdf`
