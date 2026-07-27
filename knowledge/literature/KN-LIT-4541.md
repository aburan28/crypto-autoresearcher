---
id: KN-LIT-4541
type: literature
title: "Inverted Edwards coordinates"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, hyperelliptic, pairing, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Edwards curves have attracted great interest for several reasons. When curve parameters are chosen properly, the addition formulas use only 10M + 1S.

## Key claims (as reported)
- The formulas are strongly unified, i.e., work without change for doublings; even better, they are complete, i.e., work without change for all inputs.
- Dedicated doubling formulas use only 3M + 4S, and dedicated tripling formulas use only 9M + 4S.
- This paper introduces inverted Edwards coordinates.
- Inverted Edwards coordinates (X1 : Y1 : Z1 ) represent the affine point (Z1 /X1 , Z1 /Y1 ) on an Edwards curve; for comparison, standard Edwards coordinates (X1 : Y1 : Z1 ) represent the affine point (X1 /Z1 , Y1 /Z1 ).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/inverted-20071009.pdf`
