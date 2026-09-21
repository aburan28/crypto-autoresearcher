---
id: KN-LIT-2502
type: literature
title: "An L(1/3 + ε) Algorithm for the Discrete Logarithm Problem for Low Degree Curves"
authors:
  - "Andreas Enge"
  - "Pierrick Gaudry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, complexity-theory, dlp, elliptic-curve, extension-field, factoring, finite-field, hyperelliptic, jacobian, number-theory, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The discrete logarithm problem in Jacobians of curves of high genus g over finite fields Fq is known to be computable with subexponential complexity Lqg (1/2, O(1)). We present an algorithm for a family of plane curves whose degrees in X and Y are low with respect to the curve genus, and suitably unbalanced.

## Key claims (as reported)
- The finite base fields are arbitrary, but their sizes should not grow too fast compared to the genus.
- For this family, the group structure can be computed in subexponential time of Lqg (1/3, O(1)), and a discrete logarithm computation takes subexponential time of Lqg (1/3 + ε, o(1)) for any positive ε.
- These runtime bounds rely on heuristics similar to the ones used in the number field sieve or the function field sieve algorithms.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150379 (1).pdf`
- `downloads/45150379 (2).pdf`
- `downloads/45150379 (3).pdf`
- `downloads/45150379.pdf`
