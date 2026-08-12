---
id: KN-LIT-1744
type: literature
title: "Module Learning With Errors and Structured"
authors:
  - "Extrapolated Dihedral Cosets"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/155"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/155"
tags: [lattice, pairing, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Module Learning With Errors (MLWE) problem is the fundamental hardness assumption underlying the key encapsulation and signature schemes ML-KEM and ML-DSA, which have been selected by NIST for post-quantum cryptography standardization. Understanding its quantum hardness is crucial for assessing the security of these standardized schemes.

## Key claims (as reported)
- Inspired by the equivalence between LWE and Extrapolated Dihedral Cosets Problem (EDCP) in [Brakerski, Kirshanova, Stehlé and Wen, PKC 2018], we show that the MLWE problem is as hard as a structured variant of the EDCP, which we refer to as the Integer Polynomial Module EDCP (IP-M-EDCP).
- This extension from EDCP to IP-M-EDCP relies crucially on the algebraic structure of the ring underlying MLWE: the extrapolation depends not only on the noise rate, but also on the ring’s degree.
- In fact, an IP-M-EDCP state forms a superposition over an exponential (in ring degree) number of possibilities.
- Our equivalence result holds for MLWE defined over power-of-two cyclotomic rings with constant module rank, a setting of particular relevance in cryptographic applications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-155.pdf`
