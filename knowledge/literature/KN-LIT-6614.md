---
id: KN-LIT-6614
type: literature
title: "Side Channel Information Set Decoding using Iterative Chunking Plaintext Recovery from the “Classic McEliece” Hardware Reference Implementation"
authors:
  - "Norman Lahr"
  - "Ruben Niederhagen"
  - "Richard Petri"
  - "Simona Samardjiska"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, ecdsa, factoring, implementation, isogeny, lattice, pairing, pqc, provable-security, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents an attack based on side-channel information and information set decoding (ISD) on the code-based Niederreiter cryptosystem and an evaluation of the practicality of the attack using an electromagnetic side channel. We start by directly adapting the timing side-channel plaintext-recovery attack by Shoufan et al. from 2010 to the constant-time implementation of the Niederreiter cryptosystem as used in the official FPGA-implementation of the NIST finalist “Classic McEliece”.

## Key claims (as reported)
- We then enhance our attack using ISD and a new technique that we call iterative chunking to further significantly reduce the number of required side-channel measurements.
- We theoretically show that our attack improvements have a significant impact on reducing the number of required side-channel measurements.
- For example, for the 256-bit security parameter set kem/mceliece6960119 of “Classic McEliece”, we improve the basic attack that requires 5415 measurements to less than 562 measurements on average to mount a successful plaintext-recovery attack.
- Further reductions can be achieved at the price of increasing the cost of the ISD computations.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491193 (1).pdf`
- `downloads/12491193.pdf`
