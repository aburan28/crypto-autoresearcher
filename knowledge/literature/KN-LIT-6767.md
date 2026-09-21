---
id: KN-LIT-6767
type: literature
title: "Speeding Up the Pollard Rho Method on Prime Fields"
authors:
  - "Jung Hee Cheon"
  - "Jin Hong"
  - "Minkyu Kim"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, endomorphism, factoring, finite-field, index-calculus, pollard-rho, prime-field, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a method to speed up the r-adding walk on multiplicative subgroups of the prime field. The r-adding walk is an iterating function used with the Pollard rho algorithm and is known to require less iterations than Pollard’s original iterating function in reaching a collision.

## Key claims (as reported)
- Our main idea is to follow through the r-adding walk with only partial information about the nodes reached.
- The trail traveled by the proposed method is a normal r-adding walk, but with significantly reduced execution time for each iteration.
- While a single iteration of most r-adding walks on Fp require a multiplication of two integers of log p size, the proposed method requires an operation of complexity only linear in log p, using a pre-computed table of size O((log p)r+1 · log log p).
- In practice, our rudimentary implementation of the proposed method increased the speed of Pollard rho with r-adding walks by a factor of more than 10 for 1024-bit random primes p.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500477 (1).pdf`
- `downloads/53500477 (2).pdf`
- `downloads/53500477 (3).pdf`
- `downloads/53500477.pdf`
