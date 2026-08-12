---
id: KN-LIT-1445
type: literature
title: "Optimizing AES-GCM on ARM Cortex-M4: A"
authors:
  - "FACE-Based Approach"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/512"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/512"
tags: [implementation, protocol, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Advanced Encryption Standard (AES) in Galois/Counter Mode (GCM) delivers both confidentiality and integrity yet poses performance and security challenges on resource-limited microcontrollers. In this paper, we present an optimized AES-GCM implementation for the ARM Cortex-M4 that combines Fixslicing AES with the FACE (Fast AES-CTR Encryption) strategy, significantly reducing redundant computations in AES-CTR.

## Key claims (as reported)
- We further examine two GHASH implementations—a 4-bit Table-based approach and a Karatsuba-based constanttime variant—to balance speed, memory usage, and resistance to timing attacks.
- Our evaluations on an STM32F4 microcontroller show that Fixslicing+FACE reduces AES-128 GCTR cycle counts by up to 19.41%, while the Table-based GHASH achieves nearly double the speed of its Karatsuba counterpart.
- These results confirm that, with the right mix of bitslicing optimizations, counter-mode caching, and lightweight polynomial multiplication, secure and efficient AES-GCM can be attained even on low-power embedded devices.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-512.pdf`
