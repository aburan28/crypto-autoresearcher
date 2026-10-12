---
id: KN-LIT-5228f3
type: literature
title: 'Too Small to Hide: Single-Trace Key Recovery from ML-KEM Key Generation'
authors:
- Vahid Jahandideh
year: 2026
venue: Cryptology ePrint Archive, Paper 2026/2137
identifiers:
  eprint: iacr:2026/2137
  arxiv: null
  doi: null
  url: https://eprint.iacr.org/2026/2137
source:
  citation: 'Vahid Jahandideh. Too Small to Hide: Single-Trace Key Recovery from ML-KEM Key Generation. Cryptology ePrint
    Archive 2026/2137, 2026.'
  url: https://eprint.iacr.org/2026/2137
tags:
- ml-kem
- pqm4
- cortex-m4
- power-analysis
- single-trace
- cbd
- ntt
- primal-lattice
confidence: reported
citation_verified: web
citation_verified_note: Primary ePrint abstract/landing-page metadata read on 2026-09-26. Full text, measurements and code
  were not independently inspected.
added: '2026-09-26'
superseded_by: null
---

## Reported result

The paper combines complementary leakage from centered-binomial sampling and the following NTT in optimized pqm4 key generation on Arm Cortex-M4. A single power trace reveals coefficient signs and magnitude hints. Using these hints in a primal lattice attack reportedly changes the ML-KEM-768 estimated BKZ block size from 624 to 129 (core-SVP costs 2^182.2 to 2^37.7). Randomizing each sampler output by a nonzero multiple of q raises the reported block size back to 611.

## Scope and evidence boundary

The 2^37.7 and 2^182.2 figures are cost-model estimates under physical power leakage, not a public-key-only attack and not measured end-to-end ML-KEM-768 key-recovery work. The abstract does not supply a complete per-key success-rate receipt.

## Research follow-up

Confirm the attack’s power-trace and lattice-solver receipts at the exact pqm4 commit; evaluate leakage after q-randomization and the 937-byte firmware increase.

Source: [https://eprint.iacr.org/2026/2137](https://eprint.iacr.org/2026/2137); ePrint received 2026-09-21. Abstract and metadata read on 2026-09-26; result not reproduced.
