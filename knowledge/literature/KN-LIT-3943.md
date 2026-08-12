---
id: KN-LIT-3943
type: literature
title: "FPGA Implementation of Pairings using"
authors:
  - "Residue Number System"
  - "Lazy Reduction"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, implementation, pairing, protocol, provable-security, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, a lot of progress has been made in the implementation of pairings in both hardware and software. In this paper, we present two FPGA-based high speed pairing designs using the Residue Number System and lazy reduction.

## Key claims (as reported)
- We show that by combining RNS, which is naturally suitable for parallel architectures, and lazy reduction, which performs one reduction for multiple multiplications, the speed of pairing computation in hardware can be largely increased.
- The results show that both designs achieve higher speed than previous designs.
- The fastest version computes an optimal ate pairing at 126-bit security level in 0.573 ms, which is 2 times faster than all previous hardware implementations at the same security level.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170422 (1).pdf`
- `downloads/69170422 (2).pdf`
- `downloads/69170422 (3).pdf`
- `downloads/69170422.pdf`
