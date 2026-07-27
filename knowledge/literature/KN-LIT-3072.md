---
id: KN-LIT-3072
type: literature
title: "Concrete Analysis of Quantum Lattice Enumeration Shi Bai1[0000−0002−0746−3054]"
authors:
  - "Tanja Lange"
  - "Tran Ngo"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hyperelliptic, lattice, pairing, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice reduction algorithms such as BKZ (Block-KorkineZolotarev) play a central role in estimating the security of lattice-based cryptography. The subroutine in BKZ which finds the shortest vector in a projected sublattice can be instantiated with enumeration algorithms.

## Key claims (as reported)
- The enumeration procedure can be seen as a depth-first search on some “enumeration tree” whose nodes denote a partial assignment of the coefficients, corresponding to lattice points as a linear combination of the lattice basis with the coefficients.
- This work provides a concrete analysis for the cost of quantum lattice enumeration based on Montanaro’s quantum tree backtracking algorithm.
- More precisely, we give a concrete implementation in the quantum circuit model.
- We also show how to optimize the circuit depth by parallelizing the components.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438240 (1).pdf`
- `downloads/14438240.pdf`
