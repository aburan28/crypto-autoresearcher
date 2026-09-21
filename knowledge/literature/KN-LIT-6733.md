---
id: KN-LIT-6733
type: literature
title: "Software implementation of Koblitz curves over quadratic fields"
authors:
  - "Thomaz Oliveira"
  - "Julio López"
  - "Francisco Rodrı́guez-Henrı́quez"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, extension-field, finite-field, implementation, prime-field, protocol, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we retake an old idea presented by Koblitz in his landmark paper [21], where he suggested the possibility of defining anomalous elliptic curves over the base field F4 . We present a careful implementation of the base and quadratic field arithmetic required for computing the scalar multiplication operation in such curves.

## Key claims (as reported)
- In order to achieve a fast reduction procedure, we adopted a redundant trinomial strategy that embeds elements of the field F4m , with m a prime number, into a ring of higher order defined by an almost irreducible trinomial.
- We also report a number of techniques that allow us to take full advantage of the native vector instructions of high-end microprocessors.
- Our software library achieves the fastest timings reported for the computation of the timing-protected scalar multiplication on Koblitz curves, and competitive timings with respect to the speed records established recently in the computation of the scalar multiplication over prime fields.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130146 (1).pdf`
- `downloads/98130146.pdf`
