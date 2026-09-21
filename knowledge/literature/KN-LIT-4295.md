---
id: KN-LIT-4295
type: literature
title: "How to Obfuscate Programs Directly"
authors:
  - "Joe Zimmerman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, glv-gls, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new way to obfuscate programs, via compositeorder multilinear maps. Our construction operates directly on straightline programs (arithmetic circuits), rather than converting them to matrix branching programs as in other known approaches.

## Key claims (as reported)
- This yields considerable efficiency improvements.
- For an NC1 circuit of size s and depth d, with n inputs, we require only O(d2 s2 + n2 ) multilinear map operations to evaluate the obfuscated circuit—as compared with other known approaches, for which the number of operations is exponential in d.
- We prove virtual black-box (VBB) security for our construction in a generic model of multilinear maps of hidden composite order, extending previous models for the prime-order setting.
- Our scheme works either with “noisy” multilinear maps, which can only evaluate expressions of degree λc for pre-specified constant c; or with “clean” multilinear maps, which can evaluate arbitrary expressions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560256 (1).pdf`
- `downloads/90560256.pdf`
