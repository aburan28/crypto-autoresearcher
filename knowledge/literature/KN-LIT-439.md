---
id: KN-LIT-439
type: literature
title: "Summation polynomial algorithms for elliptic curves in characteristic two"
authors:
  - "Steven D. Galbraith"
  - "Shishay W. Gebregiyorgis"
year: 2014
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2014/806"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2014/806"
tags: [binary-field, curve-arithmetic, dlp, ecdlp, elliptic-curve, extension-field, finite-field, index-calculus, point-decomposition, pollard-rho, semaev, summation-polynomial, survey, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The paper is about the discrete logarithm problem for elliptic curves over characteristic 2 finite fields F2n of prime degree n. We consider practical issues about index calculus attacks using summation polynomials in this setting.

## Key claims (as reported)
- The contributions of the paper include: a choice of variables for binary Edwards curves (invariant under the action of a relatively large group) to lower the degree of the summation polynomials; a choice of factor base that “breaks symmetry” and increases the probability of finding a relation; an experimental investigation of the use of SAT solvers rather than Gröbner basis methods for solving multivariate polynomial equations over F2 .
- We show that our choice of variables gives a significant improvement to previous work in this case.
- The symmetrybreaking factor base and use of SAT solvers seem to give some benefits in practice, but our experimental results are not conclusive.
- Our work indicates that Pollard rho is still much faster than index calculus algorithms for the ECDLP (and even for variants such as the oracle-assisted static Diffie-Hellman problem of Granger and Joux-Vitse) over prime extension fields F2n of reasonable size.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2014-806.pdf`
