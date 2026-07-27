---
id: KN-LIT-3193
type: literature
title: "COUNTING POINTS ON SMOOTH PLANE QUARTICS"
authors:
  - "EDGAR COSTA"
  - "DAVID HARVEY"
  - "ANDREW V. SUTHERLAND"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, elliptic-curve, hyperelliptic, number-theory, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present efficient algorithms for counting points on a smooth plane quartic curve X modulo a prime p. We address both the case where X is defined over Fp and the case where X is defined over Q and p is a prime of good reduction.

## Key claims (as reported)
- We consider two approaches for computing #X(Fp ), one which runs in O(p log p log log p) time using O(log p) space and one which runs in O(p1/2 log2 p) time using O(p1/2 log p) space.
- Both approaches yield algorithms that are faster in practice than existing methods.
- We also present average polynomial-time algorithms for X/Q that compute #X(Fp ) for good primes p ⩽ N in O(N log3 N ) time using O(N ) space.
- These are the first practical implementations of average polynomial-time algorithms for curves that are not cyclic covers of P1 , which in combination with previous results addresses all curves of genus g ⩽ 3.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ANTS-XV_costa-harvey-sutherland.pdf`
