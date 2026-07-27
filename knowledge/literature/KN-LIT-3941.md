---
id: KN-LIT-3941
type: literature
title: "FourQ on FPGA: New Hardware Speed Records for Elliptic Curve Cryptography over Large Prime Characteristic Fields"
authors:
  - "Kimmo Järvinen"
  - "Andrea Miele"
  - "Reza Azarderakhsh"
  - "Patrick Longa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, implementation, pairing, prime-field, rsa, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present fast and compact implementations of FourQ (ASIACRYPT 2015) on field-programmable gate arrays (FPGAs), and demonstrate, for the first time, the high efficiency of this new elliptic curve on reconfigurable hardware. By adapting FourQ’s algorithms to hardware, we design FPGA-tailored architectures that are significantly faster than any other ECC alternative over large prime characteristic fields.

## Key claims (as reported)
- For example, we show that our single-core and multi-core implementations can compute at a rate of 6389 and 64730 scalar multiplications per second, respectively, on a Xilinx Zynq-7020 FPGA, which represent factor-2.5 and 2 speedups in comparison with the corresponding variants of the fastest Curve25519 implementation on the same device.
- These results show the potential of deploying FourQ on hardware for high-performance and embedded security applications.
- All the presented implementations exhibit regular, constant-time execution, protecting against timing and simple side-channel attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130141 (1).pdf`
- `downloads/98130141.pdf`
