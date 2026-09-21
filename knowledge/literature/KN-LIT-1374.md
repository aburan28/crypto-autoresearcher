---
id: KN-LIT-1374
type: literature
title: "Dimensional eROSion: Improving the ROS Attack with Decomposition in Higher Bases"
authors:
  - "Antoine Joux"
  - "Julian Loss"
  - "Giacomo Santato"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/306"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/306"
tags: [elliptic-curve, mov-fr, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the polynomial attack to the ROS problem modulo p from [6]. Our new algorithm achieves a polynomial time solution in dimension l ≳ 0.725 · log2 p, extending the range of dimensions for which a polynomial attack is known beyond the previous bound of l > log2 p.

## Key claims (as reported)
- We also combine our new algorithm with Wagner’s attack to improve the general ROS attack complexity for some of the dimensions where a polynomial solution is still not known.
- We implement our polynomial attack and break the one-more unforgeability of blind Schnorr signatures over 256-bit elliptic curves in a few seconds with 192 concurrent sessions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-306 (1).pdf`
- `downloads/2025-306.pdf`
