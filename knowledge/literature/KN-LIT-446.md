---
id: KN-LIT-446
type: literature
title: "Time-Memory Trade-offs for Index Calculus in Genus"
authors:
  - "Kim Laine"
  - "Kristin Lauter"
year: 2014
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2014/346"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2014/346"
tags: [dlp, elliptic-curve, finite-field, hyperelliptic, index-calculus, isogeny, jacobian, pollard-rho]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present a variant of Diem’s e O(q) index calculus algorithm to attack the discrete logarithm problem (DLP) in Jacobians of genus 3 non-hyperelliptic curves over a finite field Fq . We implement this new variant in C++ and study the complexity in both theory and practice, making the logarithmic factors and constants hidden in the e O-notation precise.

## Key claims (as reported)
- Our variant improves the computational complexity at the cost of a moderate increase in memory consumption, but we also improve the computational complexity even when we limit the memory usage to that of Diem’s original algorithm.
- Finally, we examine how parallelization can help to reduce both the memory cost per computer and the running time for our algorithms.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2014-346.pdf`
