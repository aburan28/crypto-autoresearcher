---
id: KN-LIT-7285
type: literature
title: "Twisted Edwards Curves Revisited"
authors:
  - "Huseyin Hisil"
  - "Kenneth Koon-Ho Wong"
  - "Gary Carter"
  - "Ed Dawson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces fast algorithms for performing group operations on twisted Edwards curves, pushing the recent speed limits of Elliptic Curve Cryptography (ECC) forward in a wide range of applications. Notably, the new addition algorithm uses1 8M for suitably selected curve constants.

## Key claims (as reported)
- In comparison, the fastest point addition algorithms for (twisted) Edwards curves stated in the literature use 9M + 1S.
- It is also shown that the new addition algorithm can be implemented with four processors dropping the effective cost to 2M.
- This implies an effective speed increase by the full factor of 4 over the sequential case.
- Our results allow faster implementation of elliptic curve scalar multiplication.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500329 (1).pdf`
- `downloads/53500329 (2).pdf`
- `downloads/53500329 (3).pdf`
- `downloads/53500329.pdf`
