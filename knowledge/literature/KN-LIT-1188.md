---
id: KN-LIT-1188
type: literature
title: "A Concrete Analysis of Wagner’s k-List Algorithm over Zp"
authors:
  - "Antoine Joux"
  - "Hunter Kippen"
  - "Julian Loss"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/282"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/282"
tags: [cryptanalysis, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Since its introduction by Wagner (CRYPTO ‘02), the k-list algorithm has found significant utility in cryptanalysis. One important application thereof is in computing forgeries on several interactive signature schemes that implicitly rely on the hardness of the ROS problem formulated by Schnorr (ICICS ‘01).

## Key claims (as reported)
- The current best attack strategy for these schemes relies the conjectured runtime of the k-list algorithm over Zp .
- The tightest known analysis of Wagner’s algorithm over Zp is due to Shallue (ANTS ‘08).
- However, it hides large polynomial factors and leaves a gap with respect to desirable concrete parameters for the attack.
- In this work, we develop a degraded version of the k-list algorithm which provably enforces the heuristic invariants in Wagner’s original.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-282.pdf`
