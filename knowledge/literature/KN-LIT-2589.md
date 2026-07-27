---
id: KN-LIT-2589
type: literature
title: "Asymptotically faster quantum algorithms to solve multivariate quadratic equations"
authors:
  - "Daniel J. Bernstein"
  - "Bo-Yin Yang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, finite-field, hash, pairing, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper designs and analyzes a quantum algorithm to solve a system of m quadratic equations in n variables over a finite field Fq . In the case m = n and q = 2, under standard assumptions, the algorithm takes time 2(t+o(1))n on a mesh-connected computer of area 2(a+o(1))n , where t ≈ 0.45743 and a ≈ 0.01467.

## Key claims (as reported)
- The area-time product has asymptotic exponent t + a ≈ 0.47210.
- For comparison, the area-time product of Grover’s algorithm has asymptotic exponent 0.50000.
- Parallelizing Grover’s algorithm to reach asymptotic time exponent 0.45743 requires asymptotic area exponent 0.08514, much larger than 0.01467.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/groverxl-20171215.pdf`
