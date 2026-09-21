---
id: KN-LIT-7133
type: literature
title: "Tight Security Bounds for Double-block Hash-then-Sum MACs"
authors:
  - "Seongkwang Kim"
  - "Byeonghak Lee"
  - "Jooyoung Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we study the security of deterministic MAC constructions with a double-block internal state, captured by the doubleblock hash-then-sum (DbHtS) paradigm. Most DbHtS constructions, including PolyMAC, SUM-ECBC, PMAC-Plus, 3kf9 and LightMAC-Plus, have 2n been proved to be pseudorandom up to 2 3 queries when they are instantiated with an n-bit block cipher, while the best known generic attacks 3n require 2 4 queries.

## Key claims (as reported)
- We close this gap by proving the PRF-security of DbHtS constructions up 3n to 2 4 queries (ignoring the maximum message length).
- The core of the security proof is to refine Mirror theory that systematically estimates the number of solutions to a system of equations and non-equations, and apply it to prove the security of the finalization function.
- Then we identify security requirements of the internal hash functions to ensure 3n/4-bit security of the resulting constructions when combined with the finalization function.
- Within this framework, we prove the security of DbHtS whose internal hash function is given as the concatenation of a universal hash function using two independent keys.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105126 (1).pdf`
- `downloads/12105126.pdf`
