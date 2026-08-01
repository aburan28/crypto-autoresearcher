---
id: KN-LIT-6535
type: literature
title: "Security/Efficiency Tradeoffs for Permutation-Based Hashing"
authors:
  - "Phillip Rogaway"
  - "John Steinberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide attacks and analysis that capture a tradeoff, in the ideal-permutation model, between the speed of a permutation-based hash function and its potential security. We show that any 2n-bit to n-bit compression function will have unacceptable collision resistance it makes fewer than three n-bit permutation invocations, and any 3n-bit to 2n-bit compression function will have unacceptable security if it makes fewer than five n-bit permutation invocations.

## Key claims (as reported)
- Any rate-α hash function built from n-bit permutations can be broken, in the sense of finding preimages as well as collisions, in about N 1−α queries, where N = 2n .
- Our results provide guidance when trying to design or analyze a permutation-based hash function about the limits of what can possibly be done.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650218 (1).pdf`
- `downloads/49650218 (2).pdf`
- `downloads/49650218 (3).pdf`
- `downloads/49650218.pdf`
