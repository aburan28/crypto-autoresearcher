---
id: KN-LIT-91b680
type: literature
title: "A Survey of Chosen-Prefix Collision Attacks"
authors:
  - "Marc Stevens"
year: 2021
venue: "chapter in Computational Cryptography, CUP (revised form)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [hash-functions, chosen-prefix, collision, survey, stevens]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Survey of chosen-prefix collision (CPC) attacks on cryptographic hash
functions, i.e., attacks producing collisions for two messages with
independently chosen, arbitrary prefixes. Covers the CPC framework, the
message-differential construction, meet-in-the-middle birthday-style search,
and applications (X.509 certificates, Flame malware MD5 collision).

## Key claims (as reported)
- CPC attacks are the strongest practical collision-class attacks on MD5-class
  designs; summary of the 2009/2013 constructions and, with the 2017
  Stevens–Karpman–Peyrin work, on SHA-1.
- States the birthday-bound requirement ~2^(n/2) and the benefit of
  message-differential/multi-block techniques.

## Relevance
- Peripheral to ECDLP but a baseline for the "hash-chain" primitives used in
  the program's address/commitment machinery; no direct bearing on the
  exponent-side claims. Useful as a reference survey for choosing commitments
  (not to build custom CPC-resistant).

## Not verified here
- Full content beyond first page not re-checked; claims from abstract/header.