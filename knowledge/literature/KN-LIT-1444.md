---
id: KN-LIT-1444
type: literature
title: "Optimal Representation for Right-to-Left"
authors:
  - "Parallel Scalar Point Multiplication"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2508.07310"
  url: "https://arxiv.org/abs/2508.07310"
tags: [curve-arithmetic, elliptic-curve, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces an optimal representation for a right-to-left parallel elliptic curve scalar point multiplication. The right-to-left approach is easier to parallelize than the conventional left-to-right approach.

## Key claims (as reported)
- However, unlike the left-toright approach, there is still no work considering number representations for the right-to-left parallel calculation.
- By simplifying the implementation by Robert, we devise a mathematical model to capture the computation time of the calculation.
- Then, for any arbitrary amount of doubling time and addition time, we propose algorithms to generate representations which minimize the time in that model.
- As a result, we can show a negative result that a conventional representation like NAF is almost optimal.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2508.07310v1.pdf`
