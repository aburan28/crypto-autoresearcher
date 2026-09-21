---
id: KN-LIT-3013
type: literature
title: "Complete addition formulas for prime order elliptic curves"
authors:
  - "Joost Renes"
  - "Craig Costello"
  - "Lejla Batina"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [abelian-variety, curve-arithmetic, elliptic-curve, finite-field, jacobian, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An elliptic curve addition law is said to be complete if it correctly computes the sum of any two points in the elliptic curve group. One of the main reasons for the increased popularity of Edwards curves in the ECC community is that they can allow a complete group law that is also relatively efficient (e.g., when compared to all known addition laws on Edwards curves).

## Key claims (as reported)
- Such complete addition formulas can simplify the task of an ECC implementer and, at the same time, can greatly reduce the potential vulnerabilities of a cryptosystem.
- Unfortunately, until now, complete addition laws that are relatively efficient have only been proposed on curves of composite order and have thus been incompatible with all of the currently standardized prime order curves.
- In this paper we present optimized addition formulas that are complete on every prime order short Weierstrass curve defined over a field k with char(k) 6= 2, 3.
- Compared to their incomplete counterparts, these formulas require a larger number of field additions, but interestingly require fewer field multiplications.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650347 (1).pdf`
- `downloads/96650347.pdf`
