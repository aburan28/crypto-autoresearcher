---
id: KN-LIT-934
type: literature
title: "The Case for SIKE A Decade of the Supersingular Isogeny Problem"
authors:
  - "Craig Costello"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/543"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/543"
tags: [dlp, ecdlp, factoring, hash, index-calculus, isogeny, lattice, mov-fr, number-theory, pollard-rho, pqc, protocol, quantum, rsa, sidh-csidh, supersingular, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To mark the 10-year anniversary of supersingular isogeny Diffie-Hellman, I will touch on 10 points in defense and support of the SIKE protocol, including the rise of classical hardness, the fact that quantum computers do not seem to offer much help in solving the underlying problem, and the importance of concrete cryptanalytic clarity. In the final section I present the two SIKE challenges: $55k USD is up for grabs for the solutions of mini instances that, according to the SIKE team’s security analysis, provide significantly less than 64 bits of classical security.

## Key claims (as reported)
- I conclude by urging the proponents of other schemes to construct analogous challenge instances.
- “SIKE is a fantastic scheme, but its computation is by far the most expensive, and the problem is relatively new.
- Who knows here?” – Daniel Apon (NIST) [3].

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-543.pdf`
