---
id: KN-LIT-3330
type: literature
title: "Cryptography with Auxiliary Input and Trapdoor from Constant-Noise LPN"
authors:
  - "Yu Yu"
  - "Jiang Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Dodis, Kalai and Lovett (STOC 2009) initiated the study of the Learning Parity with Noise (LPN) problem with (static) exponentially hard-to-invert auxiliary input. In particular, they showed that under a new assumption (called Learning Subspace with Noise) the above is quasi-polynomially hard in the high (polynomially close to uniform) noise regime.

## Key claims (as reported)
- Inspired by the “sampling from subspace” technique by Yu (eprint 2009 / 467) and Goldwasser et al.
- (ITCS 2010), we show that standard LPN can work in a mode (reducible to itself) where the constant-noise LPN (by sampling its matrix from a random subspace) is robust against subexponentially hard-to-invert auxiliary input with comparable security to the underlying LPN.
- Plugging this into the framework of [DKL09], we obtain the same applications as considered in [DKL09] (i.e., CPA/CCA secure symmetric encryption schemes, average-case obfuscators, reusable and robust extractors) with resilience to a more general class of leakages, improved efficiency and better security under standard assumptions.
- As a main contribution, under constant-noise LPN with certain sub1/2 exponential hardness (i.e., 2ω(n ) for secret size n) we obtain a variant of the LPN with security on poly-logarithmic entropy sources, which in turn implies CPA/CCA secure public-key encryption (PKE) schemes and oblivious transfer (OT) protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140212 (1).pdf`
- `downloads/98140212.pdf`
