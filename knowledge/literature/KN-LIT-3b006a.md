---
id: KN-LIT-3b006a
type: literature
title: 'Incomplete Ciphertext Comparison in ML-KEM: From an IND-CCA2 Break to Key Recovery'
authors:
- Bhabani Sankar Das
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/1682
identifiers:
  eprint: iacr:2026/1682
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/1682
source:
  citation: 'Bhabani Sankar Das. Incomplete Ciphertext Comparison in ML-KEM: From an IND-CCA2 Break to Key Recovery. Cryptology
    ePrint Archive 2026/1682, 2026.'
  url: https://eprint.iacr.org/2026/1682
tags:
- ml-kem
- wolfssl
- fo-transform
- simd
- implementation-attack
- key-recovery
- plaintext-checking
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

An incomplete ciphertext comparison in vulnerable wolfSSL AVX2 and NEON ML-KEM decapsulation turns skipped v bytes into a decryption-noise oracle. Regression on measurements of that noise recovers secret coefficients without lattice reduction, even when the AVX2 backend validates all of u. The ePrint abstract reports 98.0% of 2048 ML-KEM-1024 secret coefficients at 400 ciphertexts on AVX2 and 98.5% at 600 on NEON, with full recovery at larger query counts claimed.

## Scope and evidence boundary

This is a bug in the named SIMD backends, not a flaw in FIPS 203; a reused key and observable accept/reject behavior are required. Distinguish the published partial live-binary counts from any reference-model or higher-query full-key claim; the attack also needs approximately 10^5–10^6 decapsulation queries.

## Research follow-up

Test pre-fix and patched wolfSSL binaries and retain backend, version, ciphertext count, decapsulation-query count and full-key verification.

Source: [https://eprint.iacr.org/2026/1682](https://eprint.iacr.org/2026/1682); ePrint received 2026-08-13. Abstract and metadata read on 2026-09-26; result not reproduced.
