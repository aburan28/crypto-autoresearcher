---
id: KN-LIT-703
type: literature
title: "Quantum Algorithms for the Approximate"
authors:
  - "Elena Kirshanova"
  - "Erik Mårtensson"
  - "Eamonn W. Postlethwaite"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/101"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/101"
tags: [cryptanalysis, lattice, pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Shortest Vector Problem (SVP) is one of the mathematical foundations of lattice based cryptography. Lattice sieve algorithms are amongst the foremost methods of solving SVP.

## Key claims (as reported)
- The asymptotically fastest known classical and quantum sieves solve SVP in a d-dimensional 0 lattice in 2cd+o(d) time steps with 2c d+o(d) memory for constants c, c0 .
- In this work, we give various quantum sieving algorithms that trade computational steps for memory.
- We first give a quantum analogue of the classical k-Sieve algorithm [Herold–Kirshanova–Laarhoven, PKC’18] in the Quantum Random Access Memory (QRAM) model, achieving an algorithm that heuristically solves SVP in 20.2989d+o(d) time steps using 20.1395d+o(d) memory.
- This should be compared to the state-of-the-art algorithm [Laarhoven, Ph.D Thesis, 2015] which, in the same model, solves SVP in 20.2653d+o(d) time steps and memory.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210391 (1).pdf`
- `downloads/119210391.pdf`
