---
id: KN-LIT-643
type: literature
title: "Solving ECDLP via List Decoding"
authors:
  - "Fangguo Zhang"
  - "Shengli Liu"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/795"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/795"
tags: [complexity-theory, dlp, ecdlp, elliptic-curve, finite-field, pollard-rho, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a new approach to the elliptic curve discrete logarithm problem (ECDLP). First, we construct Elliptic Codes (EC codes) from the ECDLP.

## Key claims (as reported)
- Then we propose an algorithm of finding the minimum weight codewords for algebraic geometry codes, especially for the elliptic code, via list decoding.
- Finally, with the minimum weight codewords, we show how to solve ECDLP.
- This work may provide a potential approach to speeding up the computation of ECDLP.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-795.pdf`
