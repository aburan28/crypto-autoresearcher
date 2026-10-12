---
id: KN-LIT-a5c59c
type: literature
title: "Elliptic and Hyperelliptic Curves: A Practical Security Analysis"
authors:
  - "Joppe W. Bos"
  - "Craig Costello"
  - "Andrea Miele"
year: 2014
venue: "PKC 2014, LNCS 8383, pp. 203-220; ePrint 2013/644"
identifiers:
  eprint: "iacr:2013/644"
  arxiv: null
  doi: "10.1007/978-3-642-54631-0_12"
  url: null
tags: [pollard-rho, negation-map, automorphism, p-256, bn-curve, cost-estimate, ecdlp]
confidence: reported
citation_verified: read
added: "2026-09-26"
superseded_by: null
---

## Contribution

A rho framework with every known optimisation (negation, automorphisms, fruitless-cycle handling, 2048 concurrent walks) benchmarked on NIST P-256, BN254 (j=0, order-6 automorphism; the same structure as secp256k1) and genus-2 analogues. It reports expected versus measured speed-ups and extrapolated core-years. This is the best published measurement of how much of the theoretical sqrt(6) survives on a j=0 curve.

## Key claims (as reported)

- Cycles/step (Core i7-3520M, 32-adding vs 1024-adding walk): P-256 1129/1185, BN254 1030/1296. Measured speed-up: P-256 0.947*sqrt(2), BN254 0.790*sqrt(6) (expected 6/7*sqrt(6) ~ 0.857*sqrt(6)). Core-years: P-256 3.946e24 (128.0-bit), BN254 9.486e23 (125.9-bit), Generic1271 1.736e24.

## Relevance to this program

Practical rho costs on real curves: measured negation gain 0.947·√2 on P-256 and automorphism gain 0.790·√6 on BN254 (j = 0, like secp256k1); ~1129 cycles/step on one Core i7 core for P-256. The honest-constants reference for any 'rho on curve X costs Y' claim.

## Not verified here

The full text was read during the 2026-09-26 ECDLP literature sweep. Numbers are quoted from it, not re-derived or reproduced.

## Provenance

Created 2026-09-26 from the verified bibliography behind `docs/ecdlp-literature-review-20260926.md`. Every identifier above was seen on a fetched page or index record during that sweep; none is from memory.
Supersedes KN-LIT-3665 (bulk stub or misattributed entry; see that file's `superseded_by`).
