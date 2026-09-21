---
id: KN-LIT-2659
type: literature
title: "Batch binary Edwards"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, finite-field, mov-fr, prime-field]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper sets new software speed records for high-security Diffie-Hellman computations, specifically 251-bit elliptic-curve variablebase-point scalar multiplication. In one second of computation on a $200 Core 2 Quad Q6600 CPU, this paper’s software performs 30000 251-bit scalar multiplications on the binary Edwards curve d(x + x2 + y + y 2 ) = (x + x2 )(y + y 2 ) over the field F2 [t]/(t251 + t7 + t4 + t2 + 1) where d = t57 + t54 + t44 + 1.

## Key claims (as reported)
- The paper’s field-arithmetic techniques can be applied in much more generality but have a particularly efficient interaction with the completeness of addition formulas for binary Edwards curves.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770315 (1).pdf`
- `downloads/56770315 (2).pdf`
- `downloads/56770315 (3).pdf`
- `downloads/56770315.pdf`
- `downloads/bbe-20090604.pdf`
