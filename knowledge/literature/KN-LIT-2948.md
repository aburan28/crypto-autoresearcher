---
id: KN-LIT-2948
type: literature
title: "Collision Search for Elliptic Curve Discrete Logarithm over GF(2m ) with FPGA"
authors:
  - "Guerric Meurice de Dormale"
  - "Philippe Bulens"
  - "Jean-Jacques Quisquater"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdlp, elliptic-curve, finite-field, implementation, mov-fr, pollard-rho, prime-field, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this last decade, Elliptic Curve Cryptography (ECC) has gained increasing acceptance in the industry and the academic community and has been the subject of several standards. This interest is mainly due to the high level of security with relatively small keys provided by ECC.

## Key claims (as reported)
- Indeed, no sub-exponential algorithms are known to solve the underlying hard problem: the Elliptic Curve Discrete Logarithm.
- The aim of this work is to explore the possibilities of dedicated hardware implementing the best known algorithm for generic curves: the parallelized Pollard’s ρ method.
- This problem has specific constraints and requires therefore new architectures.
- Four different strategies were investigated with different FPGA families in order to provide the best areatime product, according to the capabilities of the chosen platforms.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270378 (1).pdf`
- `downloads/47270378 (2).pdf`
- `downloads/47270378 (3).pdf`
- `downloads/47270378.pdf`
