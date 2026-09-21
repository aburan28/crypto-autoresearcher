---
id: KN-LIT-4614
type: literature
title: "Kummer strikes back: new DH speed records"
authors:
  - "Daniel J. Bernstein"
  - "Chitchanok Chuengsatiansup"
  - "Tanja Lange"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, endomorphism, glv-gls, hyperelliptic, implementation, pairing, prime-field, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper sets new speed records for high-security constanttime variable-base-point Diffie–Hellman software: 305395 Cortex-A8-slow cycles; 273349 Cortex-A8-fast cycles; 91320 Sandy Bridge cycles; 91116 Ivy Bridge cycles; 54389 Haswell cycles. The only higher speed in the literature for any of these platforms is a July 2014 claim of 89000 Ivy Bridge cycles using proprietary GLV+GLS software.

## Key claims (as reported)
- This paper’s software avoids the GLV patents and has publicly verifiable performance.
- The new speeds rely on a synergy between (1) state-of-the-art formulas for genus-2 hyperelliptic curves and (2) a modern trend towards vectorization in CPUs.
- The paper introduces several new techniques for efficient vectorization of Kummer-surface computations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730244 (1).pdf`
- `downloads/88730244 (2).pdf`
- `downloads/88730244 (3).pdf`
- `downloads/88730244.pdf`
- `downloads/kummer-20141028.pdf`
