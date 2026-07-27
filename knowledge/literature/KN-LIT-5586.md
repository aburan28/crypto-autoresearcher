---
id: KN-LIT-5586
type: literature
title: "On the Security of Tandem-DM"
authors:
  - "Ewan Fleischmann"
  - "Michael Gorski"
  - "Stefan Lucks"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide the first proof of security for Tandem-DM, one of the oldest and most well-known constructions for turning a block cipher with n-bit block length and 2n-bit key length into a 2n-bit cryptographic hash function. We prove, that when Tandem-DM is instantiated with AES-256, block length 128 bits and key length 256 bits, any adversary that asks less than 2120.4 queries cannot find a collision with success probability greater than 1/2.

## Key claims (as reported)
- We also prove a bound for preimage resistance of Tandem-DM.
- Interestingly, as there is only one practical construction known turning such an (n, 2n) bit block cipher into a 2n-bit compression function that has provably birthday-type collision resistance (FSE’06, Hirose), Tandem-DM is one out of two constructions that has this desirable feature.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650090 (1).pdf`
- `downloads/56650090 (2).pdf`
- `downloads/56650090 (3).pdf`
- `downloads/56650090.pdf`
