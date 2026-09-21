---
id: KN-LIT-4321
type: literature
title: "HyperPlonk: Plonk with Linear-Time Prover and High-Degree Custom Gates"
authors:
  - "Binyi Chen"
  - "Benedikt Bünz"
  - "Dan Boneh"
  - "Zhenfei Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, finite-field, hash, pairing, pqc, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Plonk is a widely used succinct non-interactive proof system that uses univariate polynomial commitments. Plonk is quite flexible: it supports circuits with low-degree “custom” gates as well as circuits with lookup gates (a lookup gate ensures that its input is contained in a predefined table).

## Key claims (as reported)
- For large circuits, the bottleneck in generating a Plonk proof is the need for computing a large FFT.
- We present HyperPlonk, an adaptation of Plonk to the boolean hypercube, using multilinear polynomial commitments.
- HyperPlonk retains the flexibility of Plonk but provides several additional benefits.
- First, it avoids the need for an FFT during proof generation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004171 (1).pdf`
- `downloads/14004171.pdf`
