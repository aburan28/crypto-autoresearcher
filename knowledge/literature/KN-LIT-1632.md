---
id: KN-LIT-1632
type: literature
title: "Eidolon: A Post-Quantum Signature Scheme Based on k-Colorability in the Age of Graph Neural Networks"
authors:
  - "Asmaa Cherkaoui∗"
  - "Ramón Flores"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/173"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/173"
tags: [complexity-theory, hash, lattice, pqc, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose Eidolon, a post-quantum signature scheme grounded in the NPcomplete k-colorability problem. Our construction generalizes the Goldreich Micali Wigderson zero-knowledge protocol to arbitrary k ≥ 3, applies the Fiat–Shamir transform, and uses Merkle-tree commitments to compress signatures from O(tn) to O(t log n).

## Key claims (as reported)
- We generate instances by planting a coloring while aiming to preserve the statistical profile of random graphs.
- We present an empirical security analysis of such a scheme against both classical solvers (ILP, DSatur) and a custom graph neural network (GNN) attacker.
- Experiments show that for n ≥ 60, neither approach is able to recover a valid coloring matching the planted solution, suggesting that well-engineered k-coloring instances can resist the considered classical and learning-based cryptanalytic approaches.
- These experiments indicate that the constructed instances resist the attacks considered in our evaluation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-173.pdf`
