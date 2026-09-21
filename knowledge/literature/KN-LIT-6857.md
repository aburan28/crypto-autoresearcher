---
id: KN-LIT-6857
type: literature
title: "Sub-linear Zero-Knowledge Argument for Correctness of a Shuffle"
authors:
  - "Jens Groth"
  - "Yuval Ishai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, mov-fr, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A shuffle of a set of ciphertexts is a new set of ciphertexts with the same plaintexts in permuted order. Shuffles of homomorphic encryptions are a key component in mix-nets, which in turn are used in protocols for anonymization and voting.

## Key claims (as reported)
- Since the plaintexts are encrypted it is not directly verifiable whether a shuffle is correct, and it is often necessary to prove the correctness of a shuffle using a zero-knowledge proof or argument.
- In previous zero-knowledge shuffle arguments from the literature the communication complexity grows linearly with the number of ciphertexts in the shuffle.
- We suggest the first practical shuffle argument with sub-linear communication complexity.
- Our result stems from combining previous work on shuffle arguments with ideas taken from probabilistically checkable proofs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650376 (1).pdf`
- `downloads/49650376 (2).pdf`
- `downloads/49650376 (3).pdf`
- `downloads/49650376.pdf`
