---
id: KN-LIT-7437
type: literature
title: "Using Equivalence Classes to Accelerate Solving the Discrete Logarithm Problem in a Short Interval"
authors:
  - "Steven D. Galbraith"
  - "Raminder S. Ruprai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [abelian-variety, dlp, elliptic-curve, fhe, finite-field, pairing, pollard-rho, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Pollard kangaroo method solves the discrete logarithm problem (DLP) in an interval of size N √ with heuristic average case expected running time approximately 2 N group operations. It is wellknown that the Pollard rho method can be sped-up by using equivalence classes (such as orbits of points under an efficiently computed group homomorphism), but such ideas have not been used for the DLP in an interval.

## Key claims (as reported)
- Indeed, it seems impossible to implement the standard kangaroo method with equivalence classes.
- The main result of the paper is to give an algorithm, building on work of Gaudry and Schost, to solve the DLP in an interval of size √ N with heuristic average case expected running time of close to 1.36 N group operations for groups with fast inversion.
- In practice the algorithm is not quite this fast, due to the usual problems with pseudorandom walks such as fruitless cycles.
- In addition, we present experimental results.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/60560372 (1).pdf`
- `downloads/60560372 (2).pdf`
- `downloads/60560372 (3).pdf`
- `downloads/60560372 (4).pdf`
- `downloads/60560372.pdf`
