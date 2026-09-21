---
id: KN-LIT-4716
type: literature
title: "Libra: Succinct Zero-Knowledge Proofs with Optimal Prover Computation Tiacheng Xie? , Jiaheng Zhang , Yupeng Zhang??"
authors:
  - "Charalampos Papamanthou"
  - "Dawn Song∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hash, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present Libra, the first zero-knowledge proof system that has both optimal prover time and succinct proof size/verification time. In particular, if C is the size of the circuit being proved (i) the prover time is O(C) irrespective of the circuit type; (ii) the proof size and verification time are both O(d log C) for d-depth log-space uniform circuits (such as RAM programs).

## Key claims (as reported)
- In addition Libra features an one-time trusted setup that depends only on the size of the input to the circuit and not on the circuit logic.
- Underlying Libra is a new linear-time algorithm for the prover of the interactive proof protocol by Goldwasser, Kalai and Rothblum (also known as GKR protocol), as well as an efficient approach to turn the GKR protocol to zero-knowledge using small masking polynomials.
- Not only does Libra have excellent asymptotics, but it is also efficient in practice.
- For example, our implementation shows that it takes 200 seconds to generate a proof for constructing a SHA2-based Merkle tree root on 256 leaves, outperforming all existing zero-knowledge proof systems.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940229 (1).pdf`
- `downloads/116940229.pdf`
