---
id: KN-LIT-6848
type: literature
title: "Structure-Preserving Signatures and Commitments to Group Elements"
authors:
  - "Masayuki Abe"
  - "Georg Fuchsbauer"
  - "Jens Groth"
  - "Kristiyan Haralambiev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A modular approach for cryptographic protocols leads to a simple design but often inefficient constructions. On the other hand, ad hoc constructions may yield efficient protocols at the cost of losing conceptual simplicity.

## Key claims (as reported)
- We suggest structure-preserving commitments and signatures to overcome this dilemma and provide a way to construct modular protocols with reasonable efficiency, while retaining conceptual simplicity.
- We focus on schemes in bilinear groups that preserve parts of the group structure, which makes it easy to combine them with other primitives such as non-interactive zero-knowledge proofs for bilinear groups.
- We say that a signature scheme is structure-preserving if its verification keys, signatures, and messages are elements in a bilinear group, and the verification equation is a conjunction of pairing-product equations.
- If moreover the verification keys lie in the message space, we call them automorphic.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230210 (1).pdf`
- `downloads/62230210 (2).pdf`
- `downloads/62230210 (3).pdf`
- `downloads/62230210.pdf`
