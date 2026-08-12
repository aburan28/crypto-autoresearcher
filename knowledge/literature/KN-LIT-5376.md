---
id: KN-LIT-5376
type: literature
title: "On Polynomial Functions Modulo pe and Faster Bootstrapping for Homomorphic Encryption"
authors:
  - "Robin Geelen( )"
  - "Ilia Iliashenko"
  - "Jiayi Kang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we perform a systematic study of functions f : Zpe → Zpe and categorize those functions that can be represented by a polynomial with integer coefficients. More specifically, we cover the following properties: necessary and sufficient conditions for the existence of an integer polynomial representation; computation of such a representation; and the complete set of equivalent polynomials that represent a given function.

## Key claims (as reported)
- As an application, we use the newly developed theory to speed up bootstrapping for the BGV and BFV homomorphic encryption schemes.
- The crucial ingredient underlying our improvements is the existence of null polynomials, i.e. non-zero polynomials that evaluate to zero in every point.
- We exploit the rich algebraic structure of these null polynomials to find better representations of the digit extraction function, which is the main bottleneck in bootstrapping.
- As such, we obtain sparse polynomials that have 50% fewer coefficients than the original ones.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004028 (1).pdf`
- `downloads/14004028.pdf`
