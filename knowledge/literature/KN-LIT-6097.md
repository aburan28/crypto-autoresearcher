---
id: KN-LIT-6097
type: literature
title: "Quantum Multicollision-Finding Algorithm"
authors:
  - "Akinori Hosoyamada"
  - "Yu Sasaki"
  - "Keita Xagawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, pqc, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The current paper presents a new quantum algorithm for finding multicollisions, often denoted by l-collisions, where an l-collision for a function is a set of l distinct inputs having the same output value. Although it is fundamental in cryptography, the problem of finding multicollisions has not received much attention in a quantum setting.

## Key claims (as reported)
- The tight bound of quantum query complexity for finding 2-collisions of random functions has been revealed to be Θ(N 1/3 ), where N is the size of a codomain.
- However, neither the lower nor upper bound is known for l-collisions.
- The paper first integrates the results from existing research to derive several new observations, e.g. l-collisions can be generated only with O(N 1/2 ) quantum queries for a small constant l.
- Then a new quantum algorithm is proposed, which finds an l-collision of any function that has a domain size l times larger than the codomain size.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240206 (1).pdf`
- `downloads/106240206.pdf`
