---
id: KN-LIT-5695
type: literature
title: "Out of Oddity – New Cryptanalytic Techniques against Symmetric Primitives Optimized for Integrity Proof Systems"
authors:
  - "Tim Beyne"
  - "Anne Canteaut"
  - "Itai Dinur"
  - "Maria Eichlseder"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, finite-field, hash, mpc, prime-field, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The security and performance of many integrity proof systems like SNARKs, STARKs and Bulletproofs highly depend on the underlying hash function. For this reason several new proposals have recently been developed.

## Key claims (as reported)
- These primitives obviously require an in-depth security evaluation, especially since their implementation constraints have led to less standard design approaches.
- This work compares the security levels offered by two recent families of such primitives, namely GMiMC and HadesMiMC.
- We exhibit low-complexity distinguishers against the GMiMC and HadesMiMC permutations for most parameters proposed in recently launched public challenges for STARK-friendly hash functions.
- In the more concrete setting of the sponge construction corresponding to the practical use in the ZK-STARK protocol, we present a practical collision attack on a round-reduced version of GMiMC and a preimage attack on some instances of HadesMiMC.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171297 (1).pdf`
- `downloads/12171297.pdf`
