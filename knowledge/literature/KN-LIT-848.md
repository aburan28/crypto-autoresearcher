---
id: KN-LIT-848
type: literature
title: "Complete Analysis of Implementing Isogeny-based Cryptography using Huff Form of Elliptic Curves"
authors:
  - "Suhri Kim"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/085"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/085"
tags: [curve-arithmetic, dlp, elliptic-curve, endomorphism, finite-field, isogeny, pairing, pqc, protocol, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present the analysis of Huff curves for implementing isogeny-based cryptography. In this regard, we first investigate the computational cost of the building blocks when compression functions are used for Huff curves.

## Key claims (as reported)
- We also apply the square-root Vélu formula on Huff curves and present a new formula for recovering the coefficient of the curve, from a given point on a Huff curve.
- From our implementation, the performance of Huff-SIDH and Montgomery-SIDH is almost the same, and the performance of Huff-CSIDH is 6% faster than Montgomery-CSIDH.
- We further optimized Huff-CSIDH by exploiting Edwards curves for computing the coefficient of the image curve and present the Huff-Edwards hybrid model.
- As a result, the performance of Huff-Edwards CSIDH is almost the same as Montgomery-Edwards CSIDH.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-085.pdf`
