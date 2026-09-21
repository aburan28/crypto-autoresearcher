---
id: KN-LIT-3948
type: literature
title: "Fractal: Post-Quantum and Transparent Recursive Proofs from Holography"
authors:
  - "Alessandro Chiesa"
  - "Dev Ojha"
  - "Nicholas Spooner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, pairing, pqc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new methodology to efficiently realize recursive composition of succinct non-interactive arguments of knowledge (SNARKs). Prior to this work, the only known methodology relied on pairing-based SNARKs instantiated on cycles of pairing-friendly elliptic curves, an expensive algebraic object.

## Key claims (as reported)
- Our methodology does not rely on any special algebraic objects and, moreover, achieves new desirable properties: it is post-quantum and it is transparent (the setup is public coin).
- We exploit the fact that recursive composition is simpler for SNARKs with preprocessing, and the core of our work is obtaining a preprocessing zkSNARK for rank-1 constraint satisfiability (R1CS) that is post-quantum and transparent.
- We obtain this latter by establishing a connection between holography and preprocessing in the random oracle model, and then constructing a holographic proof for R1CS.
- We experimentally validate our methodology, demonstrating feasibility in practice.4

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105343 (1).pdf`
- `downloads/12105343.pdf`
