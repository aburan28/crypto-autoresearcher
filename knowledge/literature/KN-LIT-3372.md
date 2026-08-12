---
id: KN-LIT-3372
type: literature
title: "Degenerate Curve Attacks Extending Invalid Curve Attacks to"
authors:
  - "Edwards Curves"
  - "Other Models"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, factoring, finite-field, pairing, quantum, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Invalid curve attacks are a well-known class of attacks against implementations of elliptic curve cryptosystems, in which an adversary tricks the cryptographic device into carrying out scalar multiplication not on the expected secure curve, but on some other, weaker elliptic curve of his choosing. In their original form, however, these attacks only affect elliptic curve implementations using addition and doubling formulas that are independent of at least one of the curve parameters.

## Key claims (as reported)
- This property is typically satisfied for elliptic curves in Weierstrass form but not for newer models that have gained increasing popularity in recent years, like Edwards and twisted Edwards curves.
- It has therefore been suggested (e.g. in the original paper on invalid curve attacks) that such alternate models could protect against those attacks.
- In this paper, we dispel that belief and present the first attack of this nature against (twisted) Edwards curves, Jacobi quartics, Jacobi intersections and more.
- Our attack differs from invalid curve attacks proper in that the cryptographic device is tricked into carrying out a computation not on another elliptic curve, but on a group isomorphic to the multiplicative group of the underlying base field.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96140158 (1).pdf`
- `downloads/96140158 (2).pdf`
- `downloads/96140158 (3).pdf`
- `downloads/96140158 (4).pdf`
- `downloads/96140158.pdf`
