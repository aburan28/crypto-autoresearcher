---
id: KN-LIT-3838
type: literature
title: "Faster Fp -arithmetic for Cryptographic Pairings on Barreto-Naehrig Curves"
authors:
  - "Junfeng Fan"
  - "Frederik Vercauteren⋆⋆"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, endomorphism, extension-field, finite-field, implementation, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper describes a new method to speed up Fp -arithmetic for Barreto-Naehrig (BN) curves. We explore the characteristics of the modulus defined by BN curves and choose curve parameters such that Fp multiplication becomes more efficient.

## Key claims (as reported)
- The proposed algorithm uses Montgomery reduction in a polynomial ring combined with a coefficient reduction phase using a pseudo-Mersenne number.
- With this algorithm, the performance of pairings on BN curves can be significantly improved, resulting in a factor 5.4 speed-up compared with the state-of-the-art hardware implementations.
- Using this algorithm, we implemented a pairing processor in hardware, which runs at 204 MHz and finishes one ate and R-ate pairing computation over a 256-bit BN curve in 4.22 ms and 2.91 ms, respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470240 (1).pdf`
- `downloads/57470240 (2).pdf`
- `downloads/57470240 (3).pdf`
- `downloads/57470240.pdf`
