---
id: KN-LIT-d5f69c
type: literature
title: Faster SVP in Polynomial Space
authors:
- Yansong Feng
- Yiming Gao
- Jiaqi Liu
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2084
identifiers:
  eprint: iacr:2026/2084
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2084
source:
  citation: Yansong Feng, Yiming Gao, Jiaqi Liu. Faster SVP in Polynomial Space. Cryptology ePrint Archive 2026/2084, 2026.
  url: https://eprint.iacr.org/2026/2084
tags:
- svp
- lattice
- exact-svp
- polynomial-space
- enumeration
- collision-search
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

For exact Euclidean SVP with polynomial space, the authors claim a randomized n^(n/(4e)+o(n))-time algorithm versus the n^(n/(2e)+o(n)) analysis of Kannan enumeration by Hanrot–Stehlé. Multiple difference representations of a fixed shortest vector allow a low-space collision search to replace exhaustive enumeration.

## Scope and evidence boundary

This is a comparison in the exact-SVP polynomial-space model. It is not automatically an improvement of BKZ core-SVP costs or a concrete reduction for ML-KEM, whose attack models use different resource assumptions.

## Research follow-up

Check whether the collision-search distribution and constants survive relevant moderate dimensions before changing any PQC cost estimator.

Source: [https://eprint.iacr.org/2026/2084](https://eprint.iacr.org/2026/2084); ePrint received 2026-09-18. Abstract and metadata read on 2026-09-26; result not reproduced.
