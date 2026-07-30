---
id: KN-LIT-6732
type: literature
title: "Software implementation of binary elliptic curves: impact of the carry-less multiplier on scalar multiplication Jonathan Taverne1? , Armando Faz-Hernández2 , Diego F. Aranha3??"
authors:
  - "Francisco Rodrı́guez-Henrı́quez"
  - "Darrel Hankerson"
  - "Julio López"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, curve-arithmetic, elliptic-curve, finite-field, implementation, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The availability of a new carry-less multiplication instruction in the latest Intel desktop processors significantly accelerates multiplication in binary fields and hence presents the opportunity for reevaluating algorithms for binary field arithmetic and scalar multiplication over elliptic curves. We describe how to best employ this instruction in field multiplication and the effect on performance of doubling and halving operations.

## Key claims (as reported)
- Alternate strategies for implementing inversion and half-trace are examined to restore most of their competitiveness relative to the new multiplier.
- These improvements in field arithmetic are complemented by a study on serial and parallel approaches for Koblitz and random curves, where parallelization strategies are implemented and compared.
- The contributions are illustrated with experimental results improving the state-of-the-art performance of halving and doubling-based scalar multiplication on NIST curves at the 112- and 192-bit security levels, and a new speed record for side-channel resistant scalar multiplication in a random curve at the 128-bit security level.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170109 (1).pdf`
- `downloads/69170109 (2).pdf`
- `downloads/69170109 (3).pdf`
- `downloads/69170109.pdf`
