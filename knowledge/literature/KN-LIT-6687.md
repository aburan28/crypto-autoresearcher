---
id: KN-LIT-6687
type: literature
title: "Simulation-Sound Arguments for LWE and Applications to KDM-CCA2 Security"
authors:
  - "Benoît Libert"
  - "Khoa Nguyen"
  - "Alain Passelègue"
  - "Radu Titiu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, pairing, pqc, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Naor-Yung paradigm is a well-known technique that constructs IND-CCA2-secure encryption schemes by means of non-interactive zero-knowledge proofs satisfying a notion of simulation-soundness. Until recently, it was an open problem to instantiate it under the sole Learning-With-Errors (LWE) assumption without relying on random oracles.

## Key claims (as reported)
- While the recent results of Canetti et al.
- (STOC’19) and PeikertShiehian (Crypto’19) provide a solution to this problem by applying the Fiat-Shamir transform in the standard model, the resulting constructions are extremely inefficient as they proceed via a reduction to an NP-complete problem.
- In this paper, we give a direct, non-generic method for instantiating Naor-Yung under the LWE assumption outside the random oracle model.
- Specifically, we give a direct construction of an unbounded simulation-sound NIZK argument system which, for carefully chosen parameters, makes it possible to express the equality of plaintexts encrypted under different keys in Regev’s cryptosystem.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491199 (1).pdf`
- `downloads/12491199.pdf`
