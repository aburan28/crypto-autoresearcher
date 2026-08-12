---
id: KN-LIT-5668
type: literature
title: "Optimally Secure Block Ciphers from Ideal Primitives"
authors:
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recent advances in block-cipher theory deliver security analyses in models where one or more underlying components (e.g., a function or a permutation) are ideal (i.e., randomly chosen). This paper addresses the question of finding new constructions achieving the highest possible security level under minimal assumptions in such ideal models.

## Key claims (as reported)
- We present a new block-cipher construction, derived from the Swapor-Not construction by Hoang et al.
- With n-bit block length, our construction is a secure pseudorandom permutation (PRP) against attackers making 2n−O(log n) block-cipher queries, and 2n−O(1) queries to the underlying component (which has itself domain size roughly n).
- This security level is nearly optimal.
- So far, only key-alternating ciphers have been known to achieve comparable security using O(n) independent random permutations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520265 (1).pdf`
- `downloads/94520265.pdf`
