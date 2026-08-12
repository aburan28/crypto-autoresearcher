---
id: KN-LIT-1511
type: literature
title: "A Certified Framework for Deterministic Navigation in Higher-Genus p-Isogeny Graphs"
authors:
  - "Hung T. Dang"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/007"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/007"
tags: [abelian-variety, cryptanalysis, elliptic-curve, endomorphism, factoring, isogeny, jacobian, pairing, pqc, sidh-csidh, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a deterministic framework for navigating p-isogeny graphs of genus g ≥ 2, addressing the lack of canonical and auditable primitives in higher dimensions. The framework integrates two components: the Certified p-Isogeny Step (PICS) and a Non-Decomposition Certificate (ND).

## Key claims (as reported)
- PICS constructs the unique Frobenius-compatible inseparable isogeny by extracting kernel directions from Hasse–Witt invariants and differential subresultant profiles, thereby eliminating randomized kernel selection.
- Complementarily, ND serves as an algebraic filter that rejects Jacobians compatible with product decompositions by enforcing cyclicity in the associated differential operator module.
- We prove that the rejection density scales asymptotically as O(p−1 ).
- Experimental validation using a C-based backend over 256-bit prime fields demonstrates that the certification logic incurs a relative overhead of less than 0.2% compared to the mandatory Hasse–Witt computation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-007.pdf`
