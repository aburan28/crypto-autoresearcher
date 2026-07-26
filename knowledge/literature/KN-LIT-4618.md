---
id: KN-LIT-4618
type: literature
title: "LaBRADOR: Compact Proofs for R1CS from Module-SIS"
authors:
  - "Ward Beullens"
  - "Gregor Seiler"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [glv-gls, hash, lattice, pairing, pqc, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The most compact quantum-safe proof systems for large circuits are PCP-type systems such as Ligero, Aurora, and Shockwave, that only use weak cryptographic assumptions, namely hash functions modeled as random oracles. One would expect that by allowing for stronger assumptions, such as the hardness of Module-SIS, it should be possible to design more compact proof systems.

## Key claims (as reported)
- But alas, despite considerable progress in lattice-based proofs, no such proof system was known so far.
- We rectify this situation by introducing a Lattice-Based Recursively Amortized Demonstration Of R1CS (LaBRADOR), with more compact proof sizes than known hash-based proof systems.
- At the 128 bits security level, LaBRADOR proves knowledge of a solution for an R1CS mod 264 + 1 with 220 constraints, with a proof size of only 58 KB, an order of magnitude more compact than previous quantum-safe proofs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850335 (1).pdf`
- `downloads/140850335.pdf`
