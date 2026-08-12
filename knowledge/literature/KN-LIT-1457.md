---
id: KN-LIT-1457
type: literature
title: "Qlapoti: Simple and Efficient"
authors:
  - "Riccardo Invernizzi"
  - "Marzio Mula"
  - "Sina Schaeffler"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1604"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1604"
tags: [elliptic-curve, endomorphism, isogeny, lattice, pairing, pqc, provable-security, sidh-csidh, signature, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The main building block in isogeny-based cryptography is an algorithmic version of the Deuring correspondence, called IdealToIsogeny. This algorithm takes as input left ideals of the endomorphism ring of a supersingular elliptic curve and computes the associated isogeny.

## Key claims (as reported)
- Building on ideas from QFESTA, the Clapoti framework by Page and Robert reduces this problem to solving a certain norm equation.
- The current state of the art is however unable to efficiently solve this equation, and resorts to a relaxed version of it instead.
- This impacts not only the efficiency of the IdealToIsogeny procedure, but also its success probability.
- The latter issue has to be mitigated with complex and memory-heavy rerandomization procedures, but still leaves a gap between the security analysis and the actual implementation of cryptographic schemes employing IdealToIsogeny as a subroutine.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1604.pdf`
