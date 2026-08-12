---
id: KN-LIT-6866
type: literature
title: "Subset-Restricted Random Walks for Pollard rho Method on Fpm ?"
authors:
  - "Minkyu Kim"
  - "Jung Hee Cheon"
  - "Jin Hong"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, dlp, elliptic-curve, extension-field, finite-field, hyperelliptic, implementation, index-calculus, mov-fr, pairing, pollard-rho, prime-field, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a variant of the Pollard rho method. We use an iterating function whose image size is much smaller than its domain and hence reaches a collision faster than the original iterating function.

## Key claims (as reported)
- We also explicitly show how this general method can be applied to multiplicative subgroups of finite fields with large extension degree.
- The construction for finite fields uses a distinctive feature of the normal basis representation, namely, that the p-th power of an element is just the cyclic shift of its normal basis representation, when the underlying field is of characteristic p.
- This makes our method appropriate for hardware implementations.
- On multiplicative subgroups of Fpm , our method shows time complexity advantage over the original Pollard rho method by a 3p−3 √ m. factor of approximately 4p−3 Through the MOV reduction, our method can be applied to pairingbased cryptosystems over binary or ternary fields.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430056 (1).pdf`
- `downloads/54430056 (2).pdf`
- `downloads/54430056 (3).pdf`
- `downloads/54430056.pdf`
