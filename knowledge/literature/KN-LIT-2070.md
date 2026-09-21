---
id: KN-LIT-2070
type: literature
title: "A Generic Transform from Multi-Round Interactive Proof to NIZK"
authors:
  - "Pierre-Alain Fouque ID"
  - "Adela Georgescu ID"
  - "Chen Qian"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, lattice, pairing, pqc, provable-security, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new generic transform that takes a multi-round interactive proof for the membership of a language L and outputs a non-interactive zero-knowledge proof (not of knowledge) in the common reference string model. Similar to the Fiat-Shamir transform, it requires a hash function H.

## Key claims (as reported)
- However, in our transform the zero-knowledge property is in the standard model, and the adaptive soundness is in the non-programmable random oracle model (NPROM).
- Behind this new generic transform, we build a new generic OR-composition of two multi-round interactive proofs.
- Note that the two common techniques for building OR-proofs (parallel OR-proof and sequential OR-proof) cannot be naturally extended to the multi-round setting.
- We also give a proof of security for our OR-proof in the quantum oracle model (QROM), surprisingly the security loss in QROM is independent from the number of rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940104 (1).pdf`
- `downloads/13940104.pdf`
