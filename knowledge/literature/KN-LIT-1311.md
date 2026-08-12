---
id: KN-LIT-1311
type: literature
title: "The generalized method of solving ECDLP using quantum annealing Łukasz Dzierzkowski1[0000−0002−9204−4558]"
authors: []
year: 2024
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2410.08725"
  url: "https://arxiv.org/abs/2410.08725"
tags: [cryptanalysis, dlp, ecdlp, elliptic-curve, factoring, pairing, pollard-rho, prime-field, protocol, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a generalization of a method allowing the transformation of the Elliptic Curve Discrete Logarithm Problem (ECDLP) over prime fields to the Quadratic Unconstrained Binary Optimization (QUBO) problem. The original method requires that a given elliptic curve model has complete arithmetic.

## Key claims (as reported)
- The new one has no such restriction, which is a breakthrough.
- Since the mentioned obstacle is no longer a problem, the latest version of the algorithm may be used for any elliptic curve model.
- As a result, one may use quantum annealing to solve ECDLP on any given model of elliptic curves.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2410.08725v1.pdf`
