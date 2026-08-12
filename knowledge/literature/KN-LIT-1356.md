---
id: KN-LIT-1356
type: literature
title: "Commitment Schemes Based on Module-LIP"
authors:
  - "Hengyi Luo"
  - "Kaijie Jiang"
  - "Renjie Jin"
  - "Yanbin Pan"
  - "Anyu Wang"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/431"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/431"
tags: [lattice, mov-fr, number-theory, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At EUROCRYPT 2025, Jiang et al. proposed a universal framework for constructing commitment schemes via group actions and instantiated it with the Lattice Isomorphism Problem (LIP) and the Lattice Automorphism Problem (LAP), marking the first application of LIP and LAP in cryptographic constructions beyond signature and encryption schemes. In this paper, we propose a more efficient module lattice version of Jiang et al.’s commitment schemes.

## Key claims (as reported)
- More precisely, we adapt all group-action-based components from their framework to the module lattice setting, thereby constructing commitment schemes that rely on specific instances of the module lattice isomorphism problem (moduleLIP).
- We also investigate the hardness of these module-LIP problems to provide security foundations for the schemes, while extending the theoretical foundations of lattice isomorphism problems in the context of module lattices.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-431.pdf`
