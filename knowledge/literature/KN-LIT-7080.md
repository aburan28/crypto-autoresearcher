---
id: KN-LIT-7080
type: literature
title: "The Summation-Truncation Hybrid: Reusing Discarded Bits for Free"
authors:
  - "Aldo Gunsing"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A well-established PRP-to-PRF conversion design is truncation: one evaluates an n-bit pseudorandom permutation on a certain input, and truncates the result to a bits. The construction is known to achieve tight 2n−a/2 security.

## Key claims (as reported)
- Truncation has gained popularity due to its appearance in the GCM-SIV key derivation function (ACM CCS 2015).
- This key derivation function makes four evaluations of AES, truncates the outputs to n/2 bits, and concatenates these to get a 2n-bit subkey.
- In this work, we demonstrate that truncation is wasteful.
- In more detail, we present the Summation-Truncation Hybrid (STH).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171202 (1).pdf`
- `downloads/12171202.pdf`
