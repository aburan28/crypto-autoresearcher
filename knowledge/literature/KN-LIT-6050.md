---
id: KN-LIT-6050
type: literature
title: "Pushing the Limits of High-Speed GF (2m ) Elliptic Curve Scalar Multiplication on FPGAs"
authors:
  - "Chester Rebeiro"
  - "Sujoy Sinha Roy"
  - "Debdeep Mukhopadhyay"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, finite-field, implementation, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present an FPGA implementation of a highspeed elliptic curve scalar multiplier for binary finite fields. High speeds are achieved by boosting the operating clock frequency while at the same time reducing the number of clock cycles required to do a scalar multiplication.

## Key claims (as reported)
- To increase clock frequency, the design uses optimized implementations of the underlying field primitives and a mathematically analyzed pipeline design.
- To reduce clock cycles, a new scheduling scheme is presented that allows overlapped processing of scalar bits.
- The resulting scalar multiplier is the fastest reported implementation for generic curves over binary finite fields.
- Additionally, the optimized primitives leads to area requirements that is significantly lesser compared to other highspeed implementations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280493 (1).pdf`
- `downloads/74280493 (2).pdf`
- `downloads/74280493 (3).pdf`
- `downloads/74280493.pdf`
