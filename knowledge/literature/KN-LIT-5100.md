---
id: KN-LIT-5100
type: literature
title: "New Complexity Trade-Offs for the (Multiple)"
authors:
  - "Number Field Sieve Algorithm in Non-Prime"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, extension-field, factoring, finite-field, hash, index-calculus, number-theory, pairing, prime-field, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The selection of polynomials to represent number fields crucially determines the efficiency of the Number Field Sieve (NFS) algorithm for solving the discrete logarithm in a finite field. An important recent work due to Barbulescu et al. builds upon existing works to propose two new methods for polynomial selection when the target field is a nonprime field.

## Key claims (as reported)
- These methods are called the generalised Joux-Lercier (GJL) and the Conjugation methods.
- In this work, we propose a new method (which we denote as A) for polynomial selection for the NFS algorithm in fields FQ , with Q = pn and n > 1.
- The new method both subsumes and generalises the GJL and the Conjugation methods and provides new trade-offs for both n composite and n prime.
- Let us denote the variant of the (multiple) NFS algorithm using the polynomial selection method “X” by (M)NFS-X.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650120 (1).pdf`
- `downloads/96650120.pdf`
