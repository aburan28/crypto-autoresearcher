---
id: KN-LIT-1350
type: literature
title: "Better Bounds for Finding Fixed-Degree Isogenies via Coppersmith’s Method"
authors:
  - "Marius A. Aardal"
  - "Diego F. Aranha"
  - "Yansong Feng"
  - "Yiming Gao"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1812"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1812"
tags: [cryptanalysis, elliptic-curve, endomorphism, isogeny, lattice, pairing, pqc, provable-security, quantum, sidh-csidh, signature, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hardness of finding isogenies of degree d between supersingular elliptic curves is a fundamental assumption in isogeny-based cryptography. Let E1 and E2 be supersingular elliptic curves defined over Fp2 , and let d be a smooth integer.

## Key claims (as reported)
- At CRYPTO 2024, Benčina et al. proposed an algorithm with time complexity e O(max{p1/2 , d/p5/8 }) in the 1/4 1/2 1/4 classical setting and e O(max{p , d /p }) in the quantum setting.
- In this work, we first observe that their analysis omits a sub-exponential 1/2 e factor exp(O(log3/4 p)).
- We then improve their result to O(max{p , 4/5 2/3 1/4 4/5 e exp(O(log p)) · d/p }) classically and O(max{p , exp(O(log p)) · d1/2 /p1/3 }) quantumly.
- Our approach relies on small-root bounds for Coppersmith’s method applied to a four-variable integer equation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1812.pdf`
