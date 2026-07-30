---
id: KN-LIT-1395
type: literature
title: "Generic-compatible distinguishers for linear regression based attacks"
authors:
  - "Sana Boussam‹"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1875"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1875"
tags: [side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non profiled attacks aim to recover secret information from a device without prior knowledge of its leakage model. However, most practical non profiled attacks, such as Differential Power Analysis, Correlation Power Analysis, and Linear Regression-based Attacks (LRA), still depend on a priori leakage assumptions.

## Key claims (as reported)
- Designing a generic attack that does not rely on any such assumption therefore remains an open problem and has been actively investigated by the side-channel community for more than a decade.
- Although Whitnall et al. showed in [37] that LRA can be considered generic when all predictors are included, this is not feasible in practice due to inherent multicollinearity issues and the inadequacy of classical distinguishers, which lose discriminating power when targeting injective functions.
- In this work, we overcome these limitations and propose the first fully generic-compatible non profiled attack.
- We show that using a Walsh-Hadamard basis enables generic LRA by eliminating multicollinearity and allowing all predictors to be considered without loss of precision.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1875.pdf`
