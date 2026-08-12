---
id: KN-LIT-4611
type: literature
title: "Known-Key Distinguishers on 11-Round Feistel and Collision Attacks on Its Hashing Modes"
authors:
  - "Yu Sasaki"
  - "Kan Yasuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present new attacks on the Feistel network, where each round function consists of a subkey XOR, S-boxes, and then a linear transformation (i.e., an SP round function). Our techniques are based largely on what they call the rebound attacks.

## Key claims (as reported)
- As a result, our attacks work most effectively when the S-boxes have a “good” differential property (like the inverse function x 7→ x−1 in the finite field) and when the linear transformation has an “optimal” branch number (i.e., a maximum distance separable matrix).
- We first describe known-key distinguishers on such Feistel block ciphers of up to 11 rounds, increasing significantly the number of rounds from previous work.
- We then apply our distinguishers to the Matyas-Meyer-Oseas and Miyaguchi-Preneel modes in which the Feistel ciphers are used, obtaining collision and half-collision attacks on these hash functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330405 (1).pdf`
- `downloads/67330405 (2).pdf`
- `downloads/67330405 (3).pdf`
- `downloads/67330405.pdf`
