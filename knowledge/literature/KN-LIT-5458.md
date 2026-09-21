---
id: KN-LIT-5458
type: literature
title: "On the Design of Hardware Building Blocks for Modern Lattice-Based Encryption Schemes Norman Göttert, Thomas Feller, Michael Schneider"
authors:
  - "Johannes Buchmann"
  - "Sorin Huss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, implementation, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present both a hardware and a software implementation variant of the learning with errors (LWE) based cryptosystem presented by Lindner and Peikert. This work helps in assessing the practicality of lattice-based encryption.

## Key claims (as reported)
- For the software implementation, we give a comparison between a matrix and polynomial based variant of the LWE scheme.
- This module includes multiplication in polynomial rings using Fast Fourier Transform (FFT).
- In order to implement lattice-based cryptography in an efficient way, it is crucial to apply the systems over polynomial rings.
- FFT speeds up multiplication in polynomial rings, which is the most critical operation in lattice-based cryptography, from quadratic to quasi-linear runtime.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280511 (1).pdf`
- `downloads/74280511 (2).pdf`
- `downloads/74280511 (3).pdf`
- `downloads/74280511.pdf`
