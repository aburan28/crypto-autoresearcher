---
id: KN-LIT-1599
type: literature
title: "Computing Asymptotic Bounds for the Automated Coppersmith Method via Linear Programming"
authors:
  - "Zhaopeng Ding"
  - "Zhaopeng Dai"
  - "Baofeng Wu"
  - "Yanshuo Zhang"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1027"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1027"
tags: [cryptanalysis, elliptic-curve, groebner, isogeny, lattice, pairing, pqc, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Coppersmith’s method is a foundational technique for finding small roots of modular polynomial equations, and determining asymptotic bounds for the recoverable roots is a central and challenging part of its analysis. In this paper, we transform the computation of asymptotic bounds for the Automated Coppersmith method, proposed by Meers and Nowakowski (ASIACRYPT 2023), into a linear programming problem, thereby obtaining a provably correct and explicitly computable formula.

## Key claims (as reported)
- As applications of our method, we obtain improved asymptotic bounds for five cryptanalytic settings: the Commutative Isogeny Hidden Number Problem, the Modular Inversion Hidden Number Problem, the Elliptic Curve Hidden Number Problem, the Linear Congruential Generators with unknown multiplier, and the Leveled Isogeny Problem with Hints for POKE.
- We believe that our method could be useful for evaluating the security of a broader range of cryptographic settings.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1027 (1).pdf`
- `downloads/2026-1027.pdf`
