---
id: KN-LIT-2644
type: literature
title: "Automatic Search for the Best Trails in ARX: Application to Block Cipher Speck"
authors:
  - "Alex Biryukov"
  - "Vesselin Velichkov"
  - "Yann Le Corre"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, quantum, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose the first adaptation of Matsui’s algorithm for finding the best differential and linear trails to the class of ARX ciphers. It is based on a branch-and-bound search strategy, does not use any heuristics and returns optimal results.

## Key claims (as reported)
- The practical application of the new algorithm is demonstrated on reduced round variants of block ciphers from the Speck family.
- More specifically, we report the probabilities of the best differential trails for up to 10, 9, 8, 7, and 7 rounds of Speck32, Speck48, Speck64, Speck96 and Speck128 respectively, together with the exact number of differential trails that have the best probability.
- The new results are used to compute bounds, under the Markov assumption, on the security of Speck against single-trail differential cryptanalysis.
- Finally, we propose two new ARX primitives with provable bounds against single-trail differential and linear cryptanalysis – a long standing open problem in the area of ARX design.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830275 (1).pdf`
- `downloads/97830275.pdf`
