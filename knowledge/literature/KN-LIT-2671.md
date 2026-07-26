---
id: KN-LIT-2671
type: literature
title: "BDD-based Cryptanalysis of Keystream Generators"
authors:
  - "Matthias Krause"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many of the keystream generators which are used in practice are LFSR-based in the sense that they produce the keystream according to a rule y = C(L(x)), where L(x) denotes an internal linear bitstream, produced by a small number of parallel linear feedback shift registers (LFSRs), and C denotes some nonlinear compression function. We present an nO(1) 2(1−α)/(1+α)n time bounded attack, the FBDD-attack, against LFSR-based generators, which computes the secret initial state x ∈ {0, 1}n from cn consecutive keystream bits, where α denotes the rate of information, which C reveals about the internal bitstream, and c denotes some small constant.

## Key claims (as reported)
- The algorithm uses Free Binary Decision Diagrams (FBDDs), a data structure for minimizing and manipulating Boolean functions.
- The FBDD-attack yields better bounds on the effective key length for several keystream generators of practical use, so a 0.656n bound for the self-shrinking generator, a 0.6403n bound for the A5/1 generator, used in the GSM standard, a 0.6n bound for the E0 encryption standard in the one level mode, and a 0.8823n bound for the two-level E0 generator used in the Bluetooth wireless LAN system.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/procvers (1).pdf`
- `downloads/procvers (2).pdf`
- `downloads/procvers.pdf`
