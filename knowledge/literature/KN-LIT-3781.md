---
id: KN-LIT-3781
type: literature
title: "Fast Algebraic Attacks on Stream Ciphers with Linear Feedback"
authors:
  - "Nicolas T. Courtois"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Many popular stream ciphers apply a filter/combiner to the state of one or several LFSRs. Algebraic attacks on such ciphers [10, 11] are possible, if there is a multivariate relation involving the key/state bits and the output bits.

## Key claims (as reported)
- Recent papers by Courtois, Meier, Krause and Armknecht [1, 2, 10, 11] show that such relations exist for several well known constructions of stream ciphers immune to all previously known attacks.
- In particular, they allow to break two ciphers using LFSRs and completely “well designed” Boolean functions: Toyocrypt and LILI-128, see [10, 11].
- Surprisingly, similar algebraic attacks exist also for the stateful combiner construction used in Bluetooth keystream generator E0 [1].
- More generally, in [2] it is proven that they can break in polynomial time, any combiner with a fixed number of inputs and a fixed number of memory bits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290177 (1).pdf`
- `downloads/27290177 (2).pdf`
- `downloads/27290177.pdf`
