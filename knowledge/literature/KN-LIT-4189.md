---
id: KN-LIT-4189
type: literature
title: "Hidden Stabilizers, the Isogeny To Endomorphism Ring Problem and the Cryptanalysis of pSIDH"
authors:
  - "Mingjie Chen"
  - "Muhammad Imran"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, cryptanalysis, dlp, elliptic-curve, endomorphism, isogeny, number-theory, pairing, pqc, protocol, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Isogeny to Endomorphism Ring Problem (IsERP) asks to compute the endomorphism ring of the codomain of an isogeny between supersingular curves in characteristic p given only a representation for this isogeny, i.e. some data and an algorithm to evaluate this isogeny on any torsion point. This problem plays a central role in isogeny-based cryptography; it underlies the security of pSIDH protocol (ASIACRYPT 2022) and it is at the heart of the recent attacks that broke the SIDH key exchange.

## Key claims (as reported)
- Prior to this work, no efficient algorithm was known to solve IsERP for a generic isogeny degree, the hardest case seemingly when the degree is prime.
- In this paper, we introduce a new quantum polynomial-time algorithm to solve IsERP for isogenies whose degrees are odd and have O(log log p) many prime factors.
- As main technical tools, our algorithm uses a quantum algorithm for computing hidden Borel subgroups, a group action on supersingular isogenies from EUROCRYPT 2021, various algorithms for the Deuring correspondence and a new algorithm to lift arbitrary quaternion order elements modulo an odd integer N with O(log log p) many prime factors to powersmooth elements.
- As a main consequence for cryptography, we obtain a quantum polynomialtime key recovery attack on pSIDH.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438193 (1).pdf`
- `downloads/14438193.pdf`
- `downloads/2023-779.pdf`
