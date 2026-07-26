---
id: KN-LIT-7084
type: literature
title: "The Tower Number Field Sieve"
authors:
  - "Razvan Barbulescu"
  - "Pierrick Gaudry"
  - "Thorsten Kleinjung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, extension-field, factoring, finite-field, number-theory, pairing, prime-field, semaev]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security of pairing-based crypto-systems relies on the difficulty to compute discrete logarithms in finite fields Fpn where n is a small integer larger than 1. The state-of-art algorithm is the number field sieve (NFS) together with its many variants.

## Key claims (as reported)
- When p has a special form (SNFS), as in many pairings constructions, NFS has a faster variant due to Joux and Pierrot.
- We present a new NFS variant for SNFS computations, which is better for some cryptographically relevant cases, according to a precise comparison of norm sizes.
- The new algorithm is an adaptation of Schirokauer’s variant of NFS based on tower extensions, for which we give a middlebrow presentation.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520154 (1).pdf`
- `downloads/94520154.pdf`
