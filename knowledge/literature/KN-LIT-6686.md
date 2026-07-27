---
id: KN-LIT-6686
type: literature
title: "Simulation-Extractable KZG Polynomial"
authors:
  - "Applications to HyperPlonk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
HyperPlonk is a recent SNARK proposal (Eurocrypt’23) that features a linear-time prover and supports custom gates of larger degree than Plonk. For the time being, its instantiations are only proven to be knowledge-sound (meaning that soundness is only guaranteed when the prover runs in isolation) while many applications motivate the stronger notion of simulation-extractability (SE).

## Key claims (as reported)
- Unfortunately, the most efficient SE compilers are not immediately applicable to multivariate polynomial interactive oracle proofs.
- To address this problem, we provide an instantiation of HyperPlonk for which we can prove simulation-extractability in a strong sense.
- As a crucial building block, we describe KZG-based commitments to multivariate polynomials that also provide simulationextractability while remaining as efficient as malleable ones.
- Our proofs stand in the combined algebraic group and random oracle model and ensure straight-line extractability (i.e., without rewinding).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602173 (1).pdf`
- `downloads/14602173.pdf`
