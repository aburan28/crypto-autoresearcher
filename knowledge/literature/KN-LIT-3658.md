---
id: KN-LIT-3658
type: literature
title: "Efficiently Masking Binomial Sampling at Arbitrary Orders for Lattice-Based Crypto"
authors:
  - "Tobias Schneider"
  - "Clara Paglialonga"
  - "Tobias Oder"
  - "Tim Güneysu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pqc, protocol, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
With the rising popularity of lattice-based cryptography, the Learning with Errors (LWE) problem has emerged as a fundamental core of numerous encryption and key exchange schemes. Many LWE-based schemes have in common that they require sampling from a discrete Gaussian distribution which comes with a number of challenges for the practical instantiation of those schemes.

## Key claims (as reported)
- One of these is the inclusion of countermeasures against a physical side-channel adversary.
- While several works discuss the protection of samplers against timing leaks, only few publications explore resistance against other side-channels, e.g., power.
- The most recent example of a protected binomial sampler (as used in key encapsulation mechanisms to sufficiently approximate Gaussian distributions) from CHES 2018 is restricted to a first-order adversary and cannot be easily extended to higher protection orders.
- In this work, we present the first protected binomial sampler which provides provable security against a side-channel adversary at arbitrary orders.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420216 (1).pdf`
- `downloads/114420216.pdf`
