---
id: KN-LIT-3846
type: literature
title: "Faster packed homomorphic operations and efficient circuit bootstrapping for TFHE"
authors:
  - "Ilaria Chillotti"
  - "Nicolas Gama"
  - "Mariya Georgieva"
  - "Malika Izabachène"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, implementation, lattice, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present several methods to improve the evaluation of homomorphic functions in TFHE, both for fully and for leveled homomorphic encryption. We propose two methods to manipulate packed data, in order to decrease the ciphertext expansion and optimize the evaluation of look-up tables and arbitrary functions in RingGSW based homomorphic schemes.

## Key claims (as reported)
- We also extend the automata logic, introduced in [19, 12], to the efficient leveled evaluation of weighted automata, and present a new homomorphic counter called TBSR, that supports all the elementary operations that occur in a multiplication.
- These improvements speed-up the evaluation of most arithmetic functions in a packed leveled mode, with a noise overhead that remains additive.
- We finally present a new circuit bootstrapping that converts LWE into low-noise RingGSW ciphertexts in just 137ms, which makes the leveled mode of TFHE composable, and which is fast enough to speed-up arithmetic functions, compared to the gate-by-gate bootstrapping given in [12].
- Finally, we propose concrete parameter sets and timing comparison for all our constructions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240285 (1).pdf`
- `downloads/106240285.pdf`
