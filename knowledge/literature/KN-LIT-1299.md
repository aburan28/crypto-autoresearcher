---
id: KN-LIT-1299
type: literature
title: "SIGNITC: Supersingular Isogeny Graph"
authors:
  - "Non-Interactive Timed Commitments"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1225"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1225"
tags: [elliptic-curve, endomorphism, isogeny, pairing, pqc, quantum, sidh-csidh, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Non-Interactive Timed Commitment schemes (NITC) allow to open any commitment after a specified delay tfd . This is useful for sealed bid auctions and as primitive for more complex protocols.

## Key claims (as reported)
- We present the first NITC without repeated squaring or black box algorithms like generic NIZK proofs or generic one-way functions.
- It has fast verification, almost arbitrary delay and satisfies IND-CCA hiding and perfect binding.
- Our protocol is based on isogenies between supersingular elliptic curves making it presumably quantum secure.
- It needs no trusted setup and can use a wide variety of primes.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1225.pdf`
