---
id: KN-LIT-6044
type: literature
title: "Publicly-Verifiable Deletion via Target-Collapsing Functions"
authors:
  - "James Bartusek"
  - "Dakshita Khurana"
  - "Alexander Poremba"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, lattice, mov-fr, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We build quantum cryptosystems that support publicly-verifiable deletion from standard cryptographic assumptions. We introduce targetcollapsing as a weakening of collapsing for hash functions, analogous to how second preimage resistance weakens collision resistance; that is, target-collapsing requires indistinguishability between superpositions and mixtures of preimages of an honestly sampled image.

## Key claims (as reported)
- We show that target-collapsing hashes enable publicly-verifiable deletion (PVD), proving conjectures from [Poremba, ITCS’23] and demonstrating that the Dual-Regev encryption (and corresponding fully homomorphic encryption) schemes support PVD under the LWE assumption.
- We further build on this framework to obtain a variety of primitives supporting publicly-verifiable deletion from weak cryptographic assumptions, including: – Commitments with PVD assuming the existence of injective oneway functions, or more generally, almost-regular one-way functions.
- Along the way, we demonstrate that (variants of) target-collapsing hashes can be built from almost-regular one-way functions. – Public-key encryption with PVD assuming trapdoored variants of injective (or almost-regular) one-way functions.
- We also demonstrate that the encryption scheme of [Hhan, Morimae, and Yamakawa, Eurocrypt’23] based on pseudorandom group actions has PVD. – X with PVD for X ∈ {attribute-based encryption, quantum fullyhomomorphic encryption, witness encryption, time-revocable encryption}, assuming X and trapdoored variants of injective (or almost-regular) one-way functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850440 (1).pdf`
- `downloads/140850440.pdf`
