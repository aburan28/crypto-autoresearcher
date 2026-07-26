---
id: KN-LIT-3824
type: literature
title: "Faster and Lower Memory Scalar Multiplication on Supersingular Curves in Characteristic Three"
authors:
  - "Roberto Avanzi ⋆"
  - "Clemens Heuberger ⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, endomorphism, pairing, provable-security, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe new algorithms for performing scalar multiplication on supersingular elliptic curves in characteristic three. These curves can be used in pairing-based cryptography.

## Key claims (as reported)
- Since in pairing-based protocols besides pairing computations also scalar multiplications are required, and the performance of the latter is not negligible, improving it is clearly important as well.
- The techniques presented here bring noticeable speed ups (up to 30% for methods using a variable amount of memory and up to 46.7% for methods with a small, fixed memory usage), while at the same time bringing substantial memory reductions – factors like 3 to 8 are not uncommon.
- The starting point for our methods is a structure theorem for unit groups of residue classes of a quadratic order associated to the Frobenius endomorphism of the considered curves.
- This allows us to define new digit sets whose elements are products of powers of certain generators of said groups.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65710112 (1).pdf`
- `downloads/65710112 (2).pdf`
- `downloads/65710112 (3).pdf`
- `downloads/65710112.pdf`
