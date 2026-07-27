---
id: KN-LIT-1879
type: literature
title: "SoK: PIOP-based SNARKs for General Computation"
authors:
  - "Yonghui Guan"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1133"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1133"
tags: [mpc, pairing, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many modern SNARK constructions follow a paradigm that combines a Polynomial Interactive Oracle Proof (PIOP) with an appropriate Polynomial Commitment Scheme (PCS). In this paradigm, the PIOP reduces soundness to the verification of a collection of polynomial relations that are checked though oracle queries, while the PCS enables succinct commitments to the corresponding polynomials.

## Key claims (as reported)
- Rather than transmitting the full polynomial representation, the prover commits to the polynomials and later provides evaluations at the points selected by the verifier.
- The verifier checks the consistency of these evaluation with the commitments and the prescribed polynomial relations.
- This combination of interactive polynomial queries and succinct commitments lies at the heart of the resulting argument system’s efficiency, leading to compact proofs and efficient verification procedures.
- Focusing on this paradigm, we adopt the frontend and backend decomposition of SNARKs for general computation introduced by Thaler and develop a unified framework that refines this separation at a finer granularity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1133.pdf`
