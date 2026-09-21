---
id: KN-LIT-3648
type: literature
title: "Efficient Zero-Knowledge Arguments for Arithmetic Circuits in the Discrete Log Setting?"
authors:
  - "Jonathan Bootle"
  - "Andrea Cerulli"
  - "Pyrros Chaidos"
  - "Jens Groth"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, finite-field, mov-fr, mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a zero-knowledge argument for arithmetic circuit satisfiability with a communication complexity that grows logarithmically in the size of the circuit. The round complexity is also logarithmic and for an arithmetic circuit with fan-in 2 gates the computation of the prover and verifier is linear in the size of the circuit.

## Key claims (as reported)
- The soundness of our argument relies solely on the well-established discrete logarithm assumption in prime order groups.
- At the heart of our new argument system is an efficient zero-knowledge argument of knowledge of openings of two Pedersen multicommitments satisfying an inner product relation, which is of independent interest.
- The inner product argument requires logarithmic communication, logarithmic interaction and linear computation for both the prover and the verifier.
- We also develop a scheme to commit to a polynomial and later reveal the evaluation at an arbitrary point, in a verifiable manner.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650200 (1).pdf`
- `downloads/96650200.pdf`
