---
id: KN-LIT-1023
type: literature
title: "Pairing-Friendly Elliptic Curves: Revisited"
authors:
  - "Security Concern"
year: 2022
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2212.01855"
  url: "https://arxiv.org/abs/2212.01855"
tags: [class-group, dlp, ecdlp, elliptic-curve, extension-field, factoring, finite-field, index-calculus, mov-fr, number-theory, pairing, pollard-rho, provable-security, quantum, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Major families of pairing-friendly elliptic curves, including BN, BLS12, BLS24, KSS16, and KSS18 have recently been vulnerable to number field sieve (NFS) attacks. Due to the recent attacks on discrete logs in F!! , selecting such curves became relevant again.

## Key claims (as reported)
- This paper revisited the topic of selecting pairing-friendly curves at different security levels.
- First, we expanded the classification given by Freeman et al.
- [1] by identifying new families that were not previously mentioned, such as a complete family with variable differentiation and new sparse families of curves.
- We discussed individual curves and a comprehensive framework for constructing parametric families.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2212.01855v1 (1).pdf`
- `downloads/2212.01855v1.pdf`
