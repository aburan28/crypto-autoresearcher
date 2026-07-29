---
id: KN-LIT-6093
type: literature
title: "Quantum Lattice Enumeration and Tweaking Discrete Pruning"
authors:
  - "Yoshinori Aono"
  - "Phong Q. Nguyen"
  - "Yixin Shen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, pairing, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Enumeration is a fundamental lattice algorithm. We show how to speed up enumeration on a quantum computer, which affects the security estimates of several lattice-based submissions to NIST: if T is the number√ of operations of enumeration, our quantum enumeration runs in roughly T operations.

## Key claims (as reported)
- This applies to the two most efficient forms of enumeration known in the extreme pruning setting: cylinder pruning but also discrete pruning introduced at Eurocrypt ’17.
- Our results are based on recent quantum tree algorithms by Montanaro and AmbainisKokainis.
- The discrete pruning case requires a crucial tweak: we modify the preprocessing so that the running time can be rigorously proved to be essentially optimal, which was the main open problem in discrete pruning.
- We also introduce another tweak to solve the more general problem of finding close lattice vectors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272194 (1).pdf`
- `downloads/11272194.pdf`
