---
id: KN-LIT-4163
type: literature
title: "Hardware/Software Co-design for Hyperelliptic Curve Cryptography (HECC) on the 8051 μP"
authors:
  - "Bart Preneel"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, complexity-theory, curve-arithmetic, dlp, elliptic-curve, hyperelliptic, implementation, jacobian, pairing, prime-field, protocol, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Implementing public-key cryptography on platforms with limited resources, such as microprocessors, is a challenging task. Hardware/software co-design is often the only answer to implement the computationally intensive operations with limited memory and power at an acceptable speed.

## Key claims (as reported)
- This contribution describes such a solution for Hyperelliptic Curve Cryptography (HECC).
- The proposed hardware/software co-design of the HECC system was implemented and co-simulated using the GEZEL design environment [3].
- As a low-cost platform, we chose an 8-bit 8051 microprocessor to which one small hardware co-processor was added for field multiplication.
- We show that the Jacobian scalar multiplication can be computed in 2.488 sec at 12 MHz on this platform if a minimal hardware module is added i.e. a hardware multiply-add unit.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/008 (1).pdf`
- `downloads/008 (2).pdf`
- `downloads/008 (3).pdf`
- `downloads/008.pdf`
