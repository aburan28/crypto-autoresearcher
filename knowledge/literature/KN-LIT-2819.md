---
id: KN-LIT-2819
type: literature
title: "Building Quantum-One-Way Functions from Block Ciphers: Davies-Meyer and Merkle-Damgård Constructions"
authors:
  - "Akinori Hosoyamada"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, hash, lattice, pairing, pqc, provable-security, quantum, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present hash functions that are almost optimally one-way in the quantum setting. Our hash functions are based on the MerkleDamgård construction iterating a Davies-Meyer compression function, which is built from a block cipher.

## Key claims (as reported)
- The quantum setting that we use is a natural extention of the classical ideal cipher model.
- Recent work has revealed that symmetric-key schemes using a block cipher or a public permutation, such as CBC-MAC or the Even-Mansour cipher, can get completely broken with quantum superposition attacks, in polynomial time of the block size.
- Since many of the popular schemes are built from a block cipher or a permutation, the recent findings motivate us to study such schemes that are provably secure in the quantum setting.
- Unfortunately, no such schemes are known, unless one relies on certain algebraic assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272308 (1).pdf`
- `downloads/11272308.pdf`
