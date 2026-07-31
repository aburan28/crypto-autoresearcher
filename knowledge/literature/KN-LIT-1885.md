---
id: KN-LIT-1885
type: literature
title: "Spectral Theory of Isogeny Graphs and Quantum Sampling of Secure Supersingular Elliptic Curves"
authors:
  - "Maher Mamah"
  - "Jake Doliskani"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2602.02263"
  url: "https://arxiv.org/abs/2602.02263"
tags: [elliptic-curve, endomorphism, hash, isogeny, mov-fr, mpc, pqc, provable-security, quantum, sidh-csidh, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the problem of sampling random supersingular elliptic curves with unknown endomorphism rings. This problem has recently gained considerable attention as many isogeny-based cryptographic protocols require such “secure” curves for instantation, while existing methods achieve this only in a trusted-setup setting.

## Key claims (as reported)
- We present the first provable quantum polynomial-time algorithms for sampling such curves with high probability, one of which is based on an algorithm of [BBD+ 24].
- One variant runs heuristically in Õ(log4 p) quantum gate complexity, and in Õ(log13 p) under the Generalized Riemann Hypothesis, and outputs a curve that is provably secure assuming average-case hardness of the endomorphism ring problem.
- Another variant samples uniform O-oriented curves with unknown endomorphism rings, for any imaginary quadratic order O, with security based on the hardness of Vectorization problem.
- When accompanied by an interactive quantum computation verification protocol our algorithms provide a secure instantiation of the CGL hash function and related primitives.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2602.02263v2 (1).pdf`
- `downloads/2602.02263v2 (2).pdf`
- `downloads/2602.02263v2.pdf`
