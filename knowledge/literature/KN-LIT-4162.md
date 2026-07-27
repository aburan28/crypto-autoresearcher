---
id: KN-LIT-4162
type: literature
title: "Hardware Accelerator for the Tate Pairing in Characteristic Three Based on Karatsuba-Ofman Multipliers"
authors:
  - "Jean-Luc Beuchat"
  - "Jérémie Detrey"
  - "Nicolas Estibals"
  - "Eiji Okamoto"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, finite-field, implementation, pairing, quantum, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper is devoted to the design of fast parallel accelerators for the cryptographic Tate pairing in characteristic three over supersingular elliptic curves. We propose here a novel hardware implementation of Miller’s loop based on a pipelined Karatsuba-Ofman multiplier.

## Key claims (as reported)
- Thanks to a careful selection of algorithms for computing the tower field arithmetic associated to the Tate pairing, we manage to keep the pipeline busy.
- We also describe the strategies we considered to design our parallel multiplier.
- They are included in a VHDL code generator allowing for the exploration of a wide range of operators.
- Then, we outline the architecture of a coprocessor for the Tate pairing over F3m .

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470225 (1).pdf`
- `downloads/57470225 (2).pdf`
- `downloads/57470225 (3).pdf`
- `downloads/57470225.pdf`
