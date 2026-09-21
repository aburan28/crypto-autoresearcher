---
id: KN-LIT-729
type: literature
title: "Alternative Tower Field Construction for Quantum Implementation of the AES S-box"
authors:
  - "Doyoung Chung"
  - "Seungkwang Lee"
  - "Dooho Choi"
  - "Jooyoung Lee"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/941"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/941"
tags: [cryptanalysis, ecdsa, finite-field, quantum, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Grover’s search algorithm allows a quantum adversary to find a k-bit secret key of a block cipher by making O(2k/2 ) block cipher queries. Resistance of a block cipher to such an attack is evaluated by quantum resources required to implement Grover’s oracle for the target cipher.

## Key claims (as reported)
- The quantum resources are typically estimated by the T -depth of its circuit implementation and the number of qubits used by the circuit (width).
- Since the AES S-box is the only component which requires T -gates in a quantum implementation of AES, recent research has put its focus on efficient implementation of the AES S-box.
- However, any efficient implementation with low T -depth will not be practical in the real world without considering qubit consumption of the implementation.
- In this work, we propose four methods of trade-off between time and space for the quantum implementation of the AES S-box.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2020-941.pdf`
