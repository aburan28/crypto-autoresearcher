---
id: KN-LIT-1690
type: literature
title: "Improved Dual Attack and Trapdoor Sampling via Quantum Rejection Sampling"
authors:
  - "Cong Ling"
  - "Hao Yan"
  - "Nicholas Zhao"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/979"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/979"
tags: [complexity-theory, cryptanalysis, fhe, lattice, mov-fr, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we revisit the dual attack and GPV trapdoor sampling, focusing on the lattice Gaussian sampling term, which can be a significant bottleneck in the overall complexity. We show that this sampling step can be quantumly accelerated by combining the lower bound underlying Wang and Ling’s analysis of Klein’s algorithm with the quantum rejection sampling (QRS) framework proposed by Ozols et al.

## Key claims (as reported)
- Specifically, this lower bound gives precisely the pointwise domination condition required for quantum rejection sampling when given coherent oracle access to a truncated Klein proposal distribution, which yields a quantum procedure for preparing the truncated dual q-ary lattice Gaussian with a quadratic reduction in the sampling complexity.
- The truncation radius is chosen so that the truncated distribution is negligibly close to the full lattice Gaussian in total variation distance.
- Substituting this sampler into the dual attack framework results in reduced overall attack-cost estimates.
- Compared with Pouly and Shen’s modern dual attack under the same parameter choices, our estimates reduce the attack cost by 9, 4, and 13 bits for Kyber-512, Kyber-768, and Kyber-1024, respectively.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-979.pdf`
