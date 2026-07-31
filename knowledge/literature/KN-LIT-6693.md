---
id: KN-LIT-6693
type: literature
title: "Sine Series Approximation of the Mod Function for Bootstrapping of Approximate HE"
authors:
  - "Charanjit S. Jutla"
  - "Nathan Manohar"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
While it is well known that the sawtooth function has a point-wise convergent Fourier series, the rate of convergence is not the best possible for the application of approximating the mod function in small intervals around multiples of the modulus. We show a different sine series, such that the sine series of order n has error O(2n+1 ) for approximating the mod function in -sized intervals around multiples of the modulus.

## Key claims (as reported)
- Moreover, the resulting polynomial, after Taylor series approximation of the sine function, has small coefficients, and the whole polynomial can be computed at a precision that is only slightly larger than −(2n + 1) log , the precision of approximation being sought.
- This polynomial can then be used to approximate the mod function to almost arbitrary precision, and hence allows practical CKKS-HE bootstrapping with arbitrary precision.
- We validate our approach by an implementation and obtain 100 bit precision bootstrapping as well as improvements over prior work even at lower precision.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760214 (1).pdf`
- `downloads/132760214.pdf`
