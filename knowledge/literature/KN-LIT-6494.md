---
id: KN-LIT-6494
type: literature
title: "Security Analysis of NIST CTR-DRBG"
authors:
  - "Viet Tung Hoang"
  - "Yaobin Shen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the security of CTR-DRBG, one of NIST’s recommended Pseudorandom Number Generator (PRNG) designs. Recently, Woodage and Shumow (Eurocrypt’ 19), and then Cohney et al.

## Key claims (as reported)
- (S&P’ 20) point out some potential vulnerabilities in both NIST specification and common implementations of CTR-DRBG.
- While these researchers do suggest counter-measures, the security of the patched CTR-DRBG is still questionable.
- Our work fills this gap, proving that CTR-DRBG satisfies the robustness notion of Dodis et al.
- (CCS’13), the standard security goal for PRNGs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171011 (1).pdf`
- `downloads/12171011.pdf`
