---
id: KN-LIT-4079
type: literature
title: "Generating Provable Primes Efficiently on Embedded Devices"
authors:
  - "Christophe Clavier"
  - "Benoit Feix"
  - "Loı̈c Thierry"
  - "Pascal Paillier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, lattice, pairing, protocol, provable-security, rsa, side-channel, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces new techniques to generate provable prime numbers efficiently on embedded devices such as smartcards, based on variants of Pocklington’s and the Brillhart-Lehmer-Selfridge-TuckermanWagstaff theorems. We introduce two new generators that, combined with cryptoprocessor-specific optimizations, open the way to efficient and tamper-resistant on-board generation of provable primes.

## Key claims (as reported)
- We also report practical results from our implementations.
- Both our theoretical and experimental results show that constructive methods can generate provable primes essentially as efficiently as state-of-the-art generators for probable primes based on Fermat and Miller-Rabin pseudo-tests.
- We evaluate the output entropy of our two generators and provide techniques to ensure a high level of resistance against physical attacks.
- This paper intends to provide practitioners with the first practical solutions for fast and secure generation of provable primes in embedded security devices.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930372 (1).pdf`
- `downloads/72930372 (2).pdf`
- `downloads/72930372 (3).pdf`
- `downloads/72930372.pdf`
