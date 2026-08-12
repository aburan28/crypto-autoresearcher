---
id: KN-LIT-3478
type: literature
title: "Dual Isogenies and Their Application to Public-key Compression for Isogeny-based Cryptography"
authors:
  - "Michael Naehrig"
  - "Joost Renes"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, isogeny, lattice, pairing, pqc, protocol, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The isogeny-based protocols SIDH and SIKE have received much attention for being post-quantum key agreement candidates that retain relatively small keys. A recent line of work has proposed and further improved compression of public keys, leading to the inclusion of public-key compression in the SIKE proposal for Round 2 of the NIST Post-Quantum Cryptography Standardization effort.

## Key claims (as reported)
- We show how to employ the dual isogeny to significantly increase performance of compression techniques, reducing their overhead from 160–182% to 77–86% for Alice’s key generation and from 98–104% to 59–61% for Bob’s across different SIDH parameter sets.
- For SIKE, we reduce the overhead of (1) key generation from 140–153% to 61–74%, (2) key encapsulation from 67–90% to 38–57%, and (3) decapsulation from 59–65% to 34–39%.
- This is mostly achieved by speeding up the pairing computations, which has until now been the main bottleneck, but we also improve (deterministic) basis generation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210336 (1).pdf`
- `downloads/119210336.pdf`
