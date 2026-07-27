---
id: KN-LIT-4281
type: literature
title: "HOW TO FIND SMALL FACTORS OF INTEGERS"
authors:
  - "DANIEL J. BERNSTEIN"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, dlp, elliptic-curve, factoring, hyperelliptic, number-theory, pairing, pollard-rho, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents an algorithm that, given a set of positive integers, finds all the prime factors ≤ y of each integer. If there are y/(lg y)O(1) integers, each with (lg y)O(1) bits, then the algorithm takes time (lg y)O(1) per integer, using fast multiplication of numbers with y(lg y)O(1) bits.

## Key claims (as reported)
- This paper also presents a comprehensive survey of previous methods and a survey of applications.
- The new algorithm is useful in congruence-combination methods to compute large factors, discrete logarithms, class groups, etc.; in particular, it indirectly speeds up the number field sieve.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/sf-20020923-retypeset20220327.pdf`
