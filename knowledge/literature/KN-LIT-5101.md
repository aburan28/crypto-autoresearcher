---
id: KN-LIT-5101
type: literature
title: "New Composite Operations and Precomputation Scheme for Elliptic Curve Cryptosystems over Prime Fields"
authors:
  - "Patrick Longa"
  - "Ali Miri"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, ecdsa, elliptic-curve, jacobian, pairing, prime-field, quantum, rsa, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new methodology to derive faster composite operations of the form dP + Q, where d is a small integer ≥ 2, for generic ECC scalar multiplications over prime fields. In particular, we present an efficient Doubling-Addition (DA) operation that can be exploited to accelerate most scalar multiplication methods, including multiscalar variants.

## Key claims (as reported)
- We also present a new precomputation scheme useful for window-based scalar multiplication that is shown to achieve the lowest cost among all known methods using only one inversion.
- In comparison to theremaining approaches that use none or several inversions, our scheme offers higher performance for most common I/M ratios.
- By combining the benefits of our precomputation scheme and the new DA operation, we can save up to 6.2% on the scalar multiplication using fractional wNAF.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49390230 (1).pdf`
- `downloads/49390230 (2).pdf`
- `downloads/49390230 (3).pdf`
- `downloads/49390230.pdf`
