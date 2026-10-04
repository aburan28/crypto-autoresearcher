---
id: KN-LIT-f663db
type: literature
title: "Solving the Discrete Logarithm of a 113-Bit Koblitz Curve with an FPGA Cluster"
authors:
  - "Erich Wenger"
  - "Paul Wolfger"
year: 2014
venue: "SAC 2014, LNCS 8781, pp. 363-379; ePrint 2014/368"
identifiers:
  eprint: "iacr:2014/368"
  arxiv: null
  doi: "10.1007/978-3-319-13051-4_22"
  url: null
tags: [pollard-rho, fpga, koblitz, binary-field, record, 113-bit, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

A fully unrolled, pipelined, self-sufficient rho iteration core for a 113-bit binary Koblitz curve. It was the first new ECDLP record set on FPGAs rather than CPU/Cell clusters.

## Key claims (as reported)

- 113-bit Koblitz curve solved on 18 Virtex-6 FPGAs in an extrapolated 24 days (actual run 47 days with partial availability); 165e6 iterations/s per FPGA (vs 42e6 it/s per PS3 quoted for the 112-bit prime record).

## Relevance to this program

113-bit Koblitz ECDLP solved on an FPGA cluster (18 Virtex-6). A Koblitz-curve record directly comparable to the ECC2K-130 engineering (smaller field, same Frobenius structure).

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
