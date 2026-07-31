---
id: KN-LIT-1798
type: literature
title: "Optimizing Polynomial Multiplication and"
authors:
  - "Jihoon Jang"
  - "Hanbeom Shin"
  - "Suhri Kim"
  - "Seokhie Hong"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1450"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1450"
tags: [implementation, lattice, mov-fr, pairing, pqc, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present an optimized implementation of Hamming QuasiCyclic (HQC) on the ARM Cortex-M4. We optimize (i) the polynomial multiplication and (ii) the support expansion in fixed-weight sampling, and (iii) propose an optional caching strategy that reuses the public transforms and hash recomputed under a fixed key.

## Key claims (as reported)
- For the polynomial multiplication, the fixed-constant multiplications in the Frobenius additive FFT (FAFFT) butterfly spend nearly half of their instructions on VMOV data movements between general-purpose and floating-point registers rather than arithmetic.
- Because minimizing the XOR count alone can increase the total instruction count, we propose a dirty-aware register-allocation policy and an XOR-operation reordering that reduce the VMOV count by up to 48.1% while leaving the XOR count unchanged.
- We apply these to a multiplication that combines prior FAFFT-CRT methods, and for HQC-1 we further find a 34% sparser FAFFT modulus that lowers the CRT reconstruction cost.
- For fixed-weight sampling, we rewrite the support expansion with predicated execution and 4-way unrolling, lowering the per-word cost of its inner loop from 22 to 6 cycles while remaining constant-time.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1450.pdf`
