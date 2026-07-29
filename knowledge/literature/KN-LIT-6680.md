---
id: KN-LIT-6680
type: literature
title: "Simulatable VRFs with Applications to Multi-Theorem NIZK"
authors:
  - "Melissa Chase"
  - "Anna Lysyanskaya"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces simulatable verifiable random functions (sVRF). VRFs are similar to pseudorandom functions, except that they are also verifiable: corresponding to each seed SK, there is a public key PK, and for y = FPK (x), it is possible to prove that y is indeed the value of the function seeded by SK.

## Key claims (as reported)
- A simulatable VRF is a VRF for which this proof can be simulated, so a simulator can pretend that the value of FPK (x) is any y.
- Our contributions are as follows.
- We introduce the notion of sVRF.
- We give two constructions: one from general assumptions (based on NIZK), but inefficient, just as a proof of concept; the other construction is practical and based on a special assumption about composite-order groups with bilinear maps.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220298 (1).pdf`
- `downloads/46220298 (2).pdf`
- `downloads/46220298 (3).pdf`
- `downloads/46220298.pdf`
