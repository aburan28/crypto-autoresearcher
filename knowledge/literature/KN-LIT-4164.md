---
id: KN-LIT-4164
type: literature
title: "Hardware/Software Co-Design of Elliptic Curve Cryptography on an 8051 Microcontroller Manuel Koschuch, Joachim Lechner, Andreas Weitzer, Johann Großschädl"
authors:
  - "Alexander Szekely"
  - "Stefan Tillich"
  - "Johannes Wolkerstorfer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, extension-field, finite-field, implementation, mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
8-bit microcontrollers like the 8051 still hold a considerable share of the embedded systems market and dominate in the smart card industry. The performance of 8-bit microcontrollers is often too poor for the implementation of public-key cryptography in software.

## Key claims (as reported)
- In this paper we present a minimalist hardware accelerator for enabling elliptic curve cryptography (ECC) on an 8051 microcontroller.
- We demonstrate the importance of removing system-level performance bottlenecks caused by the transfer of operands between hardware accelerator and external RAM.
- The integration of a small direct memory access (DMA) unit proves vital to exploit the full potential of the hardware accelerator.
- Our design allows to perform a scalar multiplication over the binary extension field GF(2191 ) in 118 msec at a clock frequency of 12 MHz.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/34 (1).pdf`
- `downloads/34 (2).pdf`
- `downloads/34 (3).pdf`
- `downloads/34.pdf`
