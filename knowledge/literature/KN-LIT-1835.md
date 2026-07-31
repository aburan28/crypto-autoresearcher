---
id: KN-LIT-1835
type: literature
title: "QuantumScouter: Reinforcement Learning-Based Optimization of Variational Quantum Circuits for Differential Cryptanalysis"
authors:
  - "Gilsang Ahn"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1456"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1456"
tags: [cryptanalysis, quantum, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Classical deep learning for differential cryptanalysis requires millions of ciphertext pairs, rendering attacks infeasible or easily detectable. This work overcomes this data limitation by introducing quantum differential distinguishers, enabling a practical attacker model where executing few queries is feasible.

## Key claims (as reported)
- We design these distinguishers via quantum machine learning based on variational quantum circuits.
- To address circuit design challenges, we propose QuantumScouter, a reinforcement learning method that discovers compact quantum circuits.
- Unlike prior work, QuantumScouter explicitly targets metrics like gate count and circuit depth, producing circuits suitable for noisy intermediate-scale quantum hardware.
- We apply QuantumScouter to the SPECK32/64 and SIMON32/64 ciphers.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1456.pdf`
