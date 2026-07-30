---
id: KN-LIT-1459
type: literature
title: "Quantum circuit for implementing AES S-box with low costs"
authors:
  - "Huinan Chen"
  - "Binbin Cai"
  - "Fei Gao"
  - "Song Lin"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/454"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/454"
tags: [cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Advanced Encryption Standard (AES) is one of the most widely used and extensively studied encryption algorithms globally, which is renowned for its efficiency and robust resistance to attacks. In this paper, three quantum circuits are designed to implement the S-box, which is the sole nonlinear component in AES.

## Key claims (as reported)
- By incorporating a linear key schedule, we achieve a quantum circuit for implementing AES with the minimum number of qubits used.
- As a consequence, only 264/328/398 qubits are needed to implement the quantum circuits for AES-128/192/256.
- Furthermore, through quantum circuits of the S-box and key schedule, the overall size of the quantum circuit required for Grover’s algorithm to attack AES is significantly decreased.
- This enhancement improves both the security and resource efficiency of AES in a quantum computing environment.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-454.pdf`
