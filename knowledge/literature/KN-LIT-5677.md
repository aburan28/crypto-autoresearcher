---
id: KN-LIT-5677
type: literature
title: "Optimized Method for Computing Odd-Degree Isogenies on Edwards Curves"
authors:
  - "Suhri Kim"
  - "Kisoon Yoon"
  - "Young-Ho Park"
  - "Seokhie Hong"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, elliptic-curve, finite-field, isogeny, pairing, pqc, protocol, quantum, sidh-csidh, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present an efficient method to compute arbitrary odd-degree isogenies on Edwards curves. By using the w-coordinate, we optimized the isogeny formula on Edwards curves by Moody and Shumow.

## Key claims (as reported)
- We demonstrate that Edwards curves have an additional benefit when recovering the coefficient of the image curve during isogeny computation.
- For `-degree isogeny where ` = 2s + 1, our isogeny formula on Edwards curves outperforms Montgomery curves when s ≥ 2.
- To better represent the performance improvements when w-coordinate is used, we implement CSIDH using our isogeny formula.
- Our implementation is about 20% faster than the previous implementation.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210173 (1).pdf`
- `downloads/119210173.pdf`
