---
id: KN-LIT-828
type: literature
title: "TWISTED μ4 -NORMAL FORM FOR ELLIPTIC CURVES DAVID KOHEL"
authors:
  - "AIX MARSEILLE UNIV"
  - "CENTRALE MARSEILLE"
year: 2020
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2012.10799"
  url: "https://arxiv.org/abs/2012.10799"
tags: [binary-field, curve-arithmetic, elliptic-curve, endomorphism, finite-field, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the twisted μ4 -normal form for elliptic curves, deriving in particular addition algorithms with complexity 9M+2S and doubling algorithms with complexity 2M + 5S + 2m over a binary field. Every ordinary elliptic curve over a finite field of characteristic 2 is isomorphic to one in this family.

## Key claims (as reported)
- This improvement to the addition algorithm, applicable to a larger class of curves, is comparable to the 7M + 2S achieved for the μ4 -normal form, and replaces the previously best known complexity of 13M + 3S on López-Dahab models applicable to these twisted curves.
- The derived doubling algorithm is essentially optimal, without any assumption of special cases.
- We show moreover that the Montgomery scalar multiplication with point recovery carries over to the twisted models, giving symmetric scalar multiplication adapted to protect against side channel attacks, with a cost of 4M + 4S + 1mt + 2mc per bit.
- In characteristic different from 2, we establish a linear isomorphism with the twisted Edwards model over the base field.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210211 (1).pdf`
- `downloads/10210211.pdf`
- `downloads/2012.10799v1.pdf`
