---
id: KN-LIT-6081
type: literature
title: "Quantum circuits for the CSIDH: optimizing quantum evaluation of isogenies"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Chloe Martindale"
  - "Lorenz Panny"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, hyperelliptic, implementation, isogeny, pairing, pqc, protocol, quantum, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Choosing safe post-quantum parameters for the new CSIDH isogeny-based key-exchange system requires concrete analysis of the cost of quantum attacks. The two main contributions to attack cost are the number of queries in hidden-shift algorithms and the cost of each query.

## Key claims (as reported)
- This paper analyzes algorithms for each query, introducing several new speedups while showing that some previous claims were too optimistic for the attacker.
- This paper includes a full computer-verified simulation of its main algorithm down to the bit-operation level.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760273 (1).pdf`
- `downloads/114760273.pdf`
- `downloads/qisog-20190305.pdf`
