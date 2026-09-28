---
id: KN-LIT-86e435
type: literature
title: "Energy-Efficient ARM64 Cluster with Cryptanalytic Applications: 80 Cores That Do Not Cost You an ARM and a Leg"
authors:
  - "Thom Wiggers"
year: 2017
venue: "LATINCRYPT 2017, pp. 175-188 (2019); ePrint 2018/888"
identifiers:
  eprint: "iacr:2018/888"
  arxiv: null
  doi: "10.1007/978-3-030-25283-0_10"
  url: null
tags: [pollard-rho, arm, cluster, energy, hardware, ecdlp]
confidence: reported
citation_verified: web
added: "2026-09-26"
superseded_by: null
---

## Contribution

Ports the "Breaking ECC2K-130" rho software to Cortex-A53 NEON, using microbenchmarks to recover undocumented instruction timings, and compares a US$1500, 80-core ODROID-C2 cluster against CPUs, GPUs and FPGAs.

## Key claims (as reported)

- 20 ODROID-C2 boards (80 cores) for < US$1500; per-platform comparison in paper.

## Relevance to this program

Energy-efficient ARM64 cluster for cryptanalysis (Pollard rho among workloads); comparison point for energy-per-iteration reporting.

## Not verified here

Only the bibliographic record and the abstract or summary page were read, fetched from IACR ePrint, arXiv, Crossref or the publisher on 2026-09-26. The full text was not read, so claims are relayed and not re-derived. Where the summary says "standard statement" or "metadata only", treat the claim as recalled until someone reads the paper.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
