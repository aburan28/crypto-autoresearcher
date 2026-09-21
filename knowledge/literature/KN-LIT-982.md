---
id: KN-LIT-982
type: literature
title: "FPGA Acceleration of Multi-Scalar Multiplication: CycloneMSM Kaveh Aasaraai, Don Beaver, Emanuele Cesena, Rahul Maganti"
authors:
  - "Nicolas Stalder"
  - "Javier Varela"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1396"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1396"
tags: [curve-arithmetic, ecdsa, elliptic-curve, endomorphism, fhe, implementation, pairing, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-Scalar Multiplication (MSM) on elliptic curves is one of the primitives and bottlenecks at the core of many zero-knowledge proof systems. Speeding up MSM typically results in faster proof generation, which in turn makes ZK-based applications practical.

## Key claims (as reported)
- We focus on accelerating large MSM on FPGA, and we present speed records for BLS12-377 on FPGA: 5.66s for N = 226 , sub-second for N = 222 .
- We developed a fully pipelined curve adder in extended Twisted Edwards coordinates that runs at 250MHz.
- Our architecture incorporates a scheduler to reorder curve operations, that’s suitable not just for hardware acceleration, but also for software implementations using affine coordinates with batch inversion.
- The software implementation achieves +10 − 20% performance improvement over the state-of-the-art gnark-crypto library.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-1396.pdf`
