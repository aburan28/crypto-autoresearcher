---
id: KN-LIT-830
type: literature
title: "Zero-Knowledge IOPs with"
authors:
  - "Linear-Time Prover"
  - "Polylogarithmic-Time Verifier ⋆"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/152"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/152"
tags: [hash, pairing, pqc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Interactive oracle proofs (IOPs) are a multi-round generalization of probabilistically checkable proofs that play a fundamental role in the construction of efficient cryptographic proofs. We present an IOP that simultaneously achieves the properties of zero knowledge, linear-time proving, and polylogarithmic-time verification.

## Key claims (as reported)
- We construct a zero-knowledge IOP where, for the satisfiability of an N -gate arithmetic circuit over any field of size Ω(N ), the prover uses O(N ) field operations and the verifier uses polylog(N ) field operations (with proof length O(N ) and query complexity polylog(N )).
- Polylogarithmic verification is achieved in the holographic setting for every circuit (the verifier has oracle access to a linear-time-computable encoding of the circuit whose satisfiability is being proved).
- Our result implies progress on a basic goal in the area of efficient zero knowledge.
- Via a known transformation, we obtain a zero knowledge argument system where the prover runs in linear time and the verifier runs in polylogarithmic time; the construction is plausibly post-quantum and only makes a black-box use of lightweight cryptography (collision-resistant hash functions).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760101 (1).pdf`
- `downloads/132760101.pdf`
