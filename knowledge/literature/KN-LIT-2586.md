---
id: KN-LIT-2586
type: literature
title: "Asymptotic complexities of discrete logarithm algorithms in pairing-relevant finite fields"
authors:
  - "Gabrielle De Micheli"
  - "Pierrick Gaudry"
  - "Cécile Pierrot"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, extension-field, factoring, finite-field, number-theory, pairing, pollard-rho, pqc, prime-field, protocol, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the discrete logarithm problem at the boundary case between small and medium characteristic finite fields, which is precisely the area where finite fields used in pairing-based cryptosystems live. In order to evaluate the security of pairing-based protocols, we thoroughly analyze the complexity of all the algorithms that coexist at this boundary case: the Quasi-Polynomial algorithms, the Number Field Sieve and its many variants, and the Function Field Sieve.

## Key claims (as reported)
- We adapt the latter to the particular case where the extension degree is composite, and show how to lower the complexity by working in a shifted function field.
- All this study finally allows us to give precise values for the characteristic asymptotically achieving the highest security level for pairings.
- Surprisingly enough, there exist special characteristics that are as secure as general ones.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171078 (1).pdf`
- `downloads/12171078.pdf`
