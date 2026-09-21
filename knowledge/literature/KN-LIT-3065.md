---
id: KN-LIT-3065
type: literature
title: "Computing the RSA Secret Key is Deterministic"
authors:
  - "Polynomial Time Equivalent to Factoring"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We address one of the most fundamental problems concerning the RSA cryptoscheme: Does the knowledge of the RSA public key/ secret key pair (e, d) yield the factorization of N = pq in polynomial time? It is well-known that there is a probabilistic polynomial time algorithm that on input (N, e, d) outputs the factors p and q.

## Key claims (as reported)
- We present the first deterministic polynomial time algorithm that factors N provided that e, d < φ(N ) and that the factors p, q are of the same bit-size.
- Our approach is an application of Coppersmith’s technique for finding small roots of bivariate integer polynomials.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/det (1).pdf`
- `downloads/det (2).pdf`
- `downloads/det.pdf`
