---
id: KN-LIT-4174
type: literature
title: "Hawk: Module LIP makes Lattice Signatures Fast, Compact and Simple"
authors:
  - "Léo Ducas"
  - "Eamonn W. Postlethwaite"
  - "Ludo N. Pulles"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, pqc, provable-security, quantum, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose the signature scheme Hawk, a concrete instantiation of proposals to use the Lattice Isomorphism Problem (LIP) as a foundation for cryptography that focuses on simplicity. This simplicity stems from LIP, which allows the use of lattices such as Zn , leading to signature algorithms with no floats, no rejection sampling, and compact precomputed distributions.

## Key claims (as reported)
- Such design features are desirable for constrained devices, and when computing signatures inside FHE or MPC.
- The most significant change from recent LIP proposals is the use of module lattices, reusing algorithms and ideas from NTRUSign and Falcon.
- Its simplicity makes Hawk competitive.
- We provide cryptanalysis with experimental evidence for the design of Hawk and implement two parameter sets, Hawk-512 and Hawk-1024.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910165 (1).pdf`
- `downloads/137910165.pdf`
