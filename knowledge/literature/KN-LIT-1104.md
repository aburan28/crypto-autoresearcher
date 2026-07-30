---
id: KN-LIT-1104
type: literature
title: "Efficient Computation of (3n , 3n )-Isogenies"
authors:
  - "Thomas Decru"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/376"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/376"
tags: [abelian-variety, cryptanalysis, dlp, elliptic-curve, endomorphism, hash, hyperelliptic, isogeny, jacobian, pqc, protocol, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The parametrization of (3, 3)-isogenies by Bruin, Flynn and Testa requires over 37.500 multiplications if one wants to evaluate a single isogeny in a point. We simplify their formulae and reduce the amount of required multiplications by 94%.

## Key claims (as reported)
- Further we deduce explicit formulae for evaluating (3, 3)-splitting and gluing maps in the framework of the parametrization by Bröker, Howe, Lauter and Stevenhagen.
- We provide implementations to compute (3n , 3n )-isogenies between principally polarized abelian surfaces with a focus on cryptographic application.
- Our implementation can retrieve Alice’s secret isogeny in 11 seconds for the SIKEp751 parameters, which were aimed at NIST level 5 security.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-376.pdf`
