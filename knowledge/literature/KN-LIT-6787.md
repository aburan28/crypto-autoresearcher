---
id: KN-LIT-6787
type: literature
title: "Stam’s collision resistance conjecture"
authors:
  - "John Steinberger ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 2008 Stam [7] made the following conjecture: if an m + s-bit to s-bit compression function F makes r calls to a primitive f of n-bit input, then a collision for F can be obtained (with high probability) using r2(nr−m)/(r+1) queries to f . For example, a 2n-bit to n-bit compression function making two calls to a random function of n-bit input cannot have collision security exceeding 2n/3 .

## Key claims (as reported)
- We prove this conjecture up to a constant multiplicative factor and under the condition m′ := (2m − n(r − 1))/(r + 1) ≥ log 2 (17).
- This covers nearly all cases r = 1 of the conjecture and the aforementioned example of a 2n-bit to n-bit compression function making two calls to a primitive of n-bit input.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320199 (1).pdf`
- `downloads/66320199 (2).pdf`
- `downloads/66320199 (3).pdf`
- `downloads/66320199.pdf`
