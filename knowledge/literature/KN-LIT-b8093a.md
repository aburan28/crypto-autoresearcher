---
id: KN-LIT-b8093a
type: literature
title: "Solving the Shortest Vector Problem in 2^{0.6039n} Time via Mid-point Hessian"
authors:
  - "Minki Hhan"
year: 2026
venue: "Cryptology ePrint Archive, Paper 2026/1597"
identifiers:
  eprint: iacr:2026/1597
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1597"
tags: [svp, lattices, hessian, gaussian-sampling, adrs, mid-point, quantum]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Randomized algorithms for the shortest vector problem. For an n-dimensional
lattice L specified by a basis, solves SVP in 2^{0.6039n+o(n)} time
classically and 2^{0.5411n+o(n)} quantumly, with space 2^{0.5n+o(n)},
improving the previous best 2^{2n+o(n)} (time and space) algorithm of
Aggarwal–Dadush–Regev–Stephens-Davidowitz (STOC 2015) at the given expense
balance.

## Key claims (as reported)
- Classical 2^{0.6039n}, quantum 2^{0.5411n}, space 2^{0.5n}.
- Uses the Hessian of the periodic Gaussian function at v/2 (eigenvector
  close to v for a shortest vector v), the parity classes in L/2L, and
  discrete Gaussian samples; optimizes with random sublattice cosets,
  achieving the final complexity.

## Relevance
- Top-tier direct SVP exponent improvement relevant to the lattice cost
  model spine the program maintains (SVP = 2^{c n} family): compare with
  the superlattice 2^{0.7314n} record in KN-LIT-b875db — this is a strictly
  smaller exponent, so it supersedes it as the classical SVP time exponent
  known to this corpus (pending peer review).
- Cross-cutting: quantum 2^{0.5411n} is also new.

## Not verified here
- Implementation/experiments not reproduced; correctness refers to the ePrint
  preprint and the claimed exponent has not been independently confirmed.