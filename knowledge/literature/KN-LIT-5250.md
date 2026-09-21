---
id: KN-LIT-5250
type: literature
title: "Numerical Method for Comparison on Homomorphically Encrypted Numbers"
authors:
  - "Jung Hee Cheon"
  - "Dongwoo Kim"
  - "Duhyeong Kim"
  - "Hun Hee Lee"
  - "Keewoo Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new method to compare numbers which are encrypted by Homomorphic Encryption (HE). Previously, comparison and min/max functions were evaluated using Boolean functions where input numbers are encrypted bit-wise.

## Key claims (as reported)
- However, the bit-wise encryption methods require relatively expensive computations for basic arithmetic operations such as addition and multiplication.
- In this paper, we introduce iterative algorithms that approximately compute the min/max and comparison operations of several numbers which are encrypted word-wise.
- From the concrete error analyses, we show that our min/max and comparison algorithms have Θ(α) and Θ(α log α) computational complexity to obtain approximate values within an error rate 2−α , while the previous minimax polynomial approximation method re√ quires the exponential complexity Θ(2α/2 ) and Θ( α·2α/2 ), respectively.
- Our algorithms achieve (quasi-)optimality in terms of asymptotic computational complexity among polynomial approximations for min/max and comparison operations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210166 (1).pdf`
- `downloads/119210166.pdf`
