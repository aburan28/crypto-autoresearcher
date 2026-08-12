---
id: KN-LIT-2678
type: literature
title: "Better Algorithms for LWE and LWR"
authors:
  - "Alexandre Duc⋆"
  - "Florian Tramèr"
  - "Serge Vaudenay"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mov-fr, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Learning With Error problem (LWE) is becoming more and more used in cryptography, for instance, in the design of some fully homomorphic encryption schemes. It is thus of primordial importance to find the best algorithms that might solve this problem so that concrete parameters can be proposed.

## Key claims (as reported)
- The BKW algorithm was proposed by Blum et al. as an algorithm to solve the Learning Parity with Noise problem (LPN), a subproblem of LWE.
- This algorithm was then adapted to LWE by Albrecht et al.
- In this paper, we improve the algorithm proposed by Albrecht et al. by using multidimensional Fourier transforms.
- Our algorithm is, to the best of our knowledge, the fastest LWE solving algorithm.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560233 (1).pdf`
- `downloads/90560233.pdf`
