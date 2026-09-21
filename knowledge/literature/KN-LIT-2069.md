---
id: KN-LIT-2069
type: literature
title: "A Generic Scheme Based on Trapdoor One-Way Permutations with Signatures as Short as Possible"
authors:
  - "Louis Granboulan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, ecdlp, elliptic-curve, pairing, provable-security, quantum, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We answer the open question of the possibility of building a digital signature scheme with proven security based on the one-wayness of a trapdoor permutation and with signatures as short as possible. Our scheme is provably secure against existential forgery under chosenmessage attacks (with tight reduction) in the ideal cipher model.

## Key claims (as reported)
- It is a variant of the construction used in QUARTZ [11], that makes multiple calls to the trapdoor permutation to avoid birthday paradox attacks.
- We name our scheme the generic chained construction (GCC) and we show that the k-rounds GCC based on a k-bit one-way permutation with k-bit security generates k-bit signatures with almost k-bit security.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33860306 (1).pdf`
- `downloads/33860306 (2).pdf`
- `downloads/33860306 (3).pdf`
- `downloads/33860306.pdf`
