---
id: KN-LIT-080
type: literature
title: Thorns in Polynomial Convolution
authors: [Dongshu Cai, Yijian Liu, Jiabo Wang, Xianhui Lu]
year: 2026
venue: Cryptology ePrint Archive, Report 2026/1022
identifiers:
  eprint: 2026/1022
  doi: null
  url: https://eprint.iacr.org/2026/1022
tags: [ml-kem, polynomial-convolution, decryption-failure, correlation, large-deviations, canonical-embedding, failure-oracle]
confidence: reported
citation_verified: full_text
added: 2026-07-23
superseded_by: null
---

> **ID remapping (2026-07-24):** originally filed as `KN-LIT-026` on the ML-KEM branch; renumbered to `KN-LIT-080` to resolve an add/add collision with `main`'s Gröbner knowledge corpus. Historical archive commits retain the old path. See `ledger/corrections/CORR-20260724-001.yaml`.


## Contribution

Studies large deviations for one product of coefficient-Gaussian polynomials
over power-of-two cyclotomics. In the canonical embedding, large-norm products
concentrate near coordinate axes; in the coefficient basis these become fixed
two-dimensional Fourier planes (“thorns”). Exact signed-partial-sum identities
explain why known LAC failure patterns align with selected embeddings.

## Verified scope

- Continuous Gaussian inputs, one polynomial product, real number-field
  arithmetic, fixed dimension, and radius tending to infinity.
- No exact theorem for ML-KEM CBD inputs, module sums, compression,
  modulo-\(q\) representatives, coefficientwise decoding, or oracle creation.
- The current revision's displayed Gaussian surrogate has second moment
  \(4\sigma^2\), while the compared product law has \(\sigma^4\); the claimed
  equal-scale comparison is therefore invalid as printed.
- Theorem 1's lower-bound polydisc has a containment gap. A fixed outward shift
  appears to repair the exponent, but the repair is not in the paper.

## ML-KEM relevance

The paper is a useful correlation-sensitive modeling lead, but it does not
change FIPS 203 failure rates, passive MLWE hardness, or conditional oracle
costs. The FIPS-cited estimator ends with a union bound over coefficients,
which does not assume coefficient independence. A claim-changing transfer
requires an exact CBD/compression one-coordinate marginal discrepancy.

Reviewed in `EV-MLKEM-003` and `DEC-20260723-005`.
