---
id: KN-LIT-1170
type: literature
title: "Simple Two-Round OT in the Explicit Isogeny Model"
authors:
  - "Emmanuela Orsini ⋆"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/269"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/269"
tags: [class-group, complexity-theory, elliptic-curve, endomorphism, isogeny, lattice, mpc, number-theory, pairing, pqc, protocol, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we apply the Type-Safe (TS) generic group model, recently introduced by Zhandry (2022), to the more general setting of group actions and extend it to the universal composability (UC) framework of Canetti (2000). We then relax this resulting model, that we call UC-TS, to define an algebraic action framework (UC-AA), where the adversaries can behave algebraically, similarly to the algebraic group model (AGM), but for group actions.

## Key claims (as reported)
- Finally, we instantiate UC-AA with isogeny-based assumptions, obtaining the Explicit-Isogeny model, UC-EI, and show that, under certain assumptions, UC-EI is less restricting that UC-AGM.
- We demonstrate the utility of our definitions by proving UC-EI security for the passive-secure protocol described by Lai et al.
- (2021), hence providing the first concretely efficient two-round isogeny-based OT protocol in the random oracle model against malicious adversaries.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-269.pdf`
