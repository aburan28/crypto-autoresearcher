---
id: KN-LIT-2459
type: literature
title: "An Algorithm to Solve the Discrete Logarithm Problem with the Number Field Sieve"
authors:
  - "An Commeine"
  - "Igor Semaev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, factoring, finite-field, index-calculus, number-theory, pollard-rho, protocol, semaev, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, Shirokauer’s algorithm to solve the discrete logarithm problem modulo a prime p has been modified by Matyukhin, yielding an algorithm with running time Lp [ 13 , 1.9018 . . .], which is, at the present time, the best known estimate of the complexity of finding discrete logarithms over prime finite fields and which coincides with the best known theoretical running time for factoring integers, obtained by Coppersmith. In this paper, another algorithm to solve the discrete logarithm problem in F∗p for p prime is presented.

## Key claims (as reported)
- The global running time is again Lp [ 13 , 1.9018 . . .], but in contrast with Matyukhins method, this algorithm enables us to calculate individual logarithms in a separate stage in time Lp [ 13 , 31/3 ], once a Lp [ 13 , 1.9018 . . .] time costing pre-computation stage has been executed.
- We describe the algorithm as derived from [6] )1/3 ], after which individual and estimate its running time to be Lp [ 13 , ( 64 9 1/3 1 logarithms can be calculated in time Lp [ 3 , 3 ].

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/39580175 (1).pdf`
- `downloads/39580175 (2).pdf`
- `downloads/39580175 (3).pdf`
- `downloads/39580175.pdf`
