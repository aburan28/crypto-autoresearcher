---
id: KN-LIT-3945
type: literature
title: "FPGA implementations of SPRING And their"
authors:
  - "Alon Rosen"
  - "François-Xavier Standaert"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, provable-security, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
SPRING is a family of pseudo-random functions that aims to combine the guarantees of security reductions with good performance on a variety of platforms. Preliminary software implementations for smallparameter instantiations of SPRING were proposed at FSE 2014, and have been demonstrated to reach throughputs within small factors of those of AES.

## Key claims (as reported)
- In this paper, we complement these results and investigate the hardware design space of these types of primitives.
- Our first (pragmatic) contribution is the first FPGA implementation of SPRING in a counter-like mode.
- We show that the “rounded product” operations in our design can be computed efficiently, reaching throughputs in the hundreds of megabits/second range within only 4% of the resources of a modern (Xilinx Virtex-6) reconfigurable device.
- Our second (more prospective) contribution is to discuss the properties of SPRING hardware implementations for side-channel resistance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310132 (1).pdf`
- `downloads/87310132 (2).pdf`
- `downloads/87310132 (3).pdf`
- `downloads/87310132.pdf`
