---
id: KN-LIT-21383c
type: literature
title: "Quantum Computation and Lattice Problems (Regev 2004)"
authors:
  - "Oded Regev"
year: 2004
venue: "SIAM Journal on Computing, 33(3):738-760"
identifiers:
  eprint: null
  doi: 10.1137/S0097539703440678
  arxiv: "cs/0304005"
  url: https://epubs.siam.org/doi/10.1137/S0097539703440678
tags: [quantum, lattice, svp, dihedral-coset-problem, dcp, dsp, hidden-subgroup, subset-sum, reduction, pqc, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-08-06
superseded_by: null
---

## Contribution
The origin of the lattices-to-dihedral-cosets connection. Two results matter
downstream:

1. A polynomial-time quantum **reduction from `a(n)`-uniqueSVP to the Dihedral
   Coset Problem** on a group of size `2N` with `N ~ 2^{n^2}` — at the cost of
   a `1/a(n)` faulty-sample rate in the DCP instance. The quadratic dimension
   blow-up was later removed by BKSW (KN-LIT-4706).
2. A polynomial-time quantum algorithm for the noise-free **Dihedral Subgroup
   Problem** that calls a **modular subset sum oracle** to erase the sample
   bits. Because the oracle is not instantiable, this is a conditional result,
   not an algorithm — but it is the template Simon 2026 (KN-LIT-e204ab) claims
   to make unconditional by replacing the erasure step.

Regev's formulation of the DSP as "given samples of
`(|0,x> + |1, x+d mod N>)/sqrt(2)`, find `d`" is the statement everything since
uses.

## Key claims (as reported)
- Lattice problems reduce quantumly to DCP, with noise rate tied to the
  approximation factor: better approximation costs a higher faulty-sample rate.
  This trade-off is exactly why noise tolerance is the decisive property of any
  DCP algorithm (KN-TECH-d1bc4f).
- DSP is in quantum polynomial time *given* a subset sum oracle.

## Relevance to this program
The foundation the Simon 2026 claim (KN-LIT-e204ab) is built on: Simon reuses
this reduction unchanged and replaces only the oracle-dependent erasure. Any
assessment of that claim needs this paper's noise/approximation trade-off to be
read carefully in the original.

## Not verified here
Paper not read. Contribution, the subset sum oracle dependency, and the
noise-rate trade-off are relayed from Simon 2026's description of it
(KN-LIT-e204ab) and from the citation metadata confirmed via search on
2026-08-06 (SIAM DOI 10.1137/S0097539703440678). Confidence `reported`
accordingly. The `n^2` dimension figure in particular is taken from Simon's
summary and should be checked against the original before use.
