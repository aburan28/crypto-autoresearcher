---
id: KN-LIT-5770
type: literature
title: "Pipelined Computation of Scalar Multiplication in Elliptic Curve Cryptosystems"
authors:
  - "Pradeep Kumar Mishra"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, finite-field, jacobian, prime-field, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the current work we propose a pipelining scheme for implementing Elliptic Curve Cryptosystems (ECC). The scalar multiplication is the dominant operation in ECC.

## Key claims (as reported)
- It is computed by a series of point additions and doublings.
- The pipelining scheme is based on a key observation: to start the subsequent operation one need not wait until the current one exits.
- The next operation can begin while a part of the current operation is still being processed.
- To our knowledge, this is the first attempt to compute the scalar multiplication in such a pipelined method.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560328 (1).pdf`
- `downloads/31560328 (2).pdf`
- `downloads/31560328.pdf`
