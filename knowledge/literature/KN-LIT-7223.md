---
id: KN-LIT-7223
type: literature
title: "Towards Practical Multi-key TFHE: Parallelizable, Key-Compatible, Quasi-linear Complexity Hyesun Kwak"
authors: []
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-key homomorphic encryption is a generalized notion of homomorphic encryption supporting arbitrary computation on ciphertexts, possibly encrypted under different keys. In this paper, we revisit the work of Chen, Chillotti and Song (ASIACRYPT 2019) and present yet another multi-key variant of the TFHE scheme.

## Key claims (as reported)
- The previous construction by Chen et al. involves a blind rotation procedure where the complexity of each iteration gradually increases as it continuously operates on ciphertexts under different keys.
- Hence, the complexity of gate bootstrapping grows quadratically with respect to the number of associated keys.
- Our scheme is based on a new blind rotation algorithm which consists of two separate phases.
- We first split a given multi-key ciphertext into several single-key ciphertexts, take each of them as input to the blind rotation procedure, and obtain accumulators corresponding to individual keys.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602006 (1).pdf`
- `downloads/14602006.pdf`
