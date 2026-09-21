---
id: KN-LIT-1933
type: literature
title: "Towards a Unified Memory-Less Framework for TCitH Jesús-Javier Chi-Domı́nguez1 , Décio"
authors:
  - "Luiz Gazzoni Filho"
  - "Marco Palumbi"
  - "and Luis Rivera-Zamarripa"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1029"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1029"
tags: [finite-field, implementation, mpc, pairing, pqc, provable-security, quantum, signature, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The current on-ramp NIST Competition for Additional PostQuantum Digital Signature Schemes features two MPCitH variants: TCitH and VOLEitH. While VOLEitH yields shorter signatures and more stack memory, making it less suitable for constrained devices.

## Key claims (as reported)
- In this work, we demonstrate that TCitH-based schemes are viable on embedded systems, such as Cortex-M4 devices.
- We present a simple, unified Zero-Knowledge Proof (ZKP) framework covering all TCitH-based submissions to the NIST competition.
- Our implementation achieves up to 99% reduction in stack usage over a baseline, with minimal code size overhead and negligible performance overhead.
- The framework is designed for extensibility: adding new schemes requires only implementing the mathematics of the underlying problem and the polynomial proof procedures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1029.pdf`
