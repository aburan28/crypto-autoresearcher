---
id: KN-LIT-2495
type: literature
title: "An Improved Algebraic Attack on Hamsi-256"
authors:
  - "Itai Dinur"
  - "Adi Shamir"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Hamsi is one of the 14 second-stage candidates in NIST’s SHA-3 competition. The only previous attack on this hash function was a very marginal attack on its 256-bit version published by Thomas Fuhr at Asiacrypt 2010, which is better than generic attacks only for very short messages of fewer than 100 32-bit blocks, and is only 26 times faster than a straightforward exhaustive search attack.

## Key claims (as reported)
- In this paper we describe a different algebraic attack which is less marginal: It is better than the best known generic attack for all practical message sizes (up to 4 gigabytes), and it outperforms exhaustive search by a factor of at least 512.
- The attack is based on the observation that in order to discard a possible second preimage, it suffices to show that one of its hashed output bits is wrong.
- Since the output bits of the compression function of Hamsi-256 can be described by low degree polynomials, it is actually faster to compute a small number of output bits by a fast polynomial evaluation technique rather than via the official algorithm.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330090 (1).pdf`
- `downloads/67330090 (2).pdf`
- `downloads/67330090 (3).pdf`
- `downloads/67330090.pdf`
