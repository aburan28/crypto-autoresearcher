---
id: KN-LIT-6188
type: literature
title: "Reducing the Number of Non-linear Multiplications in Masking Schemes"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, complexity-theory, curve-arithmetic, finite-field, implementation, mpc, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In recent years, methods to securely mask S-boxes against side-channel attacks by representing them as polynomials over finite binary fields have become quite efficient. A good cost model for this is to count how many non-linear multiplications are needed.

## Key claims (as reported)
- In this work we improve on the current state-of-the-art generic method published by Coron–Roy–Vivek at CHES 2014 by working over slightly larger fields than strictly needed.
- This leads us, for example, to evaluate DES S-boxes with only 3 non-linear multiplications and, as a result, obtain 25% improvement in the running time for secure software implementations of DES when using three or more shares.
- On the theoretical side, we prove a logarithmic upper bound on the number of non-linear multiplications required to evaluate any d-bit Sbox, when ignoring the cost of working in unreasonably large fields.
- This upper bound is lower than the previous lower bounds proved under the assumption of working over the field F2d , and we show this bound to be sharp.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130206 (1).pdf`
- `downloads/98130206.pdf`
