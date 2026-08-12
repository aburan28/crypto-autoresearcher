---
id: KN-LIT-951
type: literature
title: "An attack on SIDH with arbitrary starting curve (draft)"
authors:
  - "Luciano Maino"
  - "Chloe Martindale"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1026"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1026"
tags: [cryptanalysis, elliptic-curve, endomorphism, finite-field, isogeny, lattice, pairing, pqc, protocol, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an attack on SIDH which does not require any endomorphism information on the starting curve. Our attack has subexponential complexity thus significantly reducing the security of SIDH and SIKE; our analysis and preliminary implementation suggests that our algorithm will be feasible for the Microsoft challenge parameters p = 2110 367 − 1 on a regular computer.

## Key claims (as reported)
- Our attack applies to any isogeny-based cryptosystem that publishes the images of points under the secret isogeny, for example Séta [28] and B-SIDH [9].
- It does not apply to CSIDH [8], CSI-FiSh [3], or SQISign [11].

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-1026.pdf`
