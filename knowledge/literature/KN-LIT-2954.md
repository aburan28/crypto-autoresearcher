---
id: KN-LIT-2954
type: literature
title: "Collisions are not Incidental: A Compression Function Exploiting Discrete Geometry"
authors:
  - "Dimitar Jetchev"
  - "Onur Özen"
  - "Martijn Stam"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, mov-fr, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new construction of a compression function H : {0, 1}3n → {0, 1}2n that uses two parallel calls to an ideal primitive (an ideal blockcipher or a public random function) from 2n to n bits. This is similar to the well-known MDC-2 or the recently proposed MJH by Lee and Stam (CT-RSA’11).

## Key claims (as reported)
- However, unlike these constructions, we show already in the compression function that an adversary limited (asymptotically in n) to O(22n(1−δ)/3 ) queries (for any δ > 0) has disappearing advantage to find collisions.
- A key component of our construction is the use of the Szemerédi–Trotter theorem over finite fields to bound the number of full compression function evaluations an adversary can make, in terms of the number of queries to the underlying primitives.
- Moveover, for the security proof we rely on a new abstraction that refines and strenghtens existing techniques.
- We believe that this framework elucidates existing proofs and we consider it of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940175 (1).pdf`
- `downloads/71940175 (2).pdf`
- `downloads/71940175 (3).pdf`
- `downloads/71940175.pdf`
