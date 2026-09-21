---
id: KN-LIT-4558
type: literature
title: "J. Math. Cryptol. 2020; 14:460ś485 Research Article"
authors:
  - "Kazuhiro Yokoyama"
  - "Masaya Yasuda"
  - "Yasushi Takahashi"
  - "Jun Kogure"
year: null
venue: null
identifiers:
  eprint: null
  doi: "10.1515/jmc-2019-0029"
  arxiv: null
  url: null
tags: [binary-field, complexity-theory, dlp, ecdlp, elliptic-curve, factoring, finite-field, first-fall-degree, groebner, index-calculus, point-decomposition, pollard-rho, prime-field, rsa, semaev, summation-polynomial, supersingular, survey, weil-descent]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since Semaev introduced summation polynomials in 2004, a number of studies have been devoted to improving the index calculus method for solving the elliptic curve discrete logarithm problem (ECDLP) with better complexity than generic methods such as Pollard’s rho method and the baby-step and giant-step method (BSGS). In this paper, we provide a deep analysis of Gröbner basis computation for solving polynomial systems appearing in the point decomposition problem (PDP) in Semaev’s naive index calculus method.

## Key claims (as reported)
- Our analysis relies on linear algebra under simple statistical assumptions on summation polynomials.
- We show that the ideal derived from PDP has a special structure and Gröbner basis computation for the ideal is regarded as an extension of the extended Euclidean algorithm.
- This enables us to obtain a lower bound on the cost of Gröbner basis computation.
- With the lower bound, we prove that the naive index calculus method cannot be more efficient than generic methods.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/complexity-bounds-on-semaev-s-naive-index-calculus-method-1f7yzrgu06.pdf`
