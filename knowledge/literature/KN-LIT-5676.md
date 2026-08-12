---
id: KN-LIT-5676
type: literature
title: "Optimized Interpolation Attacks on LowMC"
authors:
  - "Itai Dinur"
  - "Yunwen Liu"
  - "Willi Meier"
  - "Qingju Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, mpc, pairing, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
LowMC is a collection of block cipher families introduced at Eurocrypt 2015 by Albrecht et al. Its design is optimized for instantiations of multi-party computation, fully homomorphic encryption, and zero-knowledge proofs.

## Key claims (as reported)
- A unique feature of LowMC is that its internal affine layers are chosen at random, and thus each block cipher family contains a huge number of instances.
- The Eurocrypt paper proposed two specific block cipher families of LowMC, having 80-bit and 128-bit keys.
- In this paper, we mount interpolation attacks (algebraic attacks introduced by Jakobsen and Knudsen) on LowMC, and show that a practically significant fraction of 2−38 of its 80-bit key instances could be broken 223 times faster than exhaustive search.
- Moreover, essentially all instances that are claimed to provide 128-bit security could be broken about 1000 times faster.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520110 (1).pdf`
- `downloads/94520110.pdf`
