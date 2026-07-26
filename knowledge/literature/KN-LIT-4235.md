---
id: KN-LIT-4235
type: literature
title: "Homomorphic Lower Digits Removal and Improved FHE Bootstrapping"
authors:
  - "Hao Chen"
  - "Kyoohyung Han"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mov-fr, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bootstrapping is a crucial operation in Gentry’s breakthrough work on fully homomorphic encryption (FHE), where a homomorphic encryption scheme evaluates its own decryption algorithm. There has been a couple of implementations of bootstrapping, among which HElib arguably marks the state-of-the-art in terms of throughput, ciphertext/message size ratio and support for large plaintext moduli.

## Key claims (as reported)
- In this work, we applied a family of “lowest digit removal” polynomials to design an improved homomorphic digit extraction algorithm which is a crucial part in bootstrapping for both FV and BGV schemes.
- When the secret key has 1-norm h = ||s||1 and the plaintext modulus is t = pr , we achieved bootstrapping depth log h + log(logp (ht)) in FV scheme.
- In case of the BGV scheme, we brought down the depth from log h + 2 log t to log h + log t.
- We implemented bootstrapping for FV in the SEAL library.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10822176 (1).pdf`
- `downloads/10822176.pdf`
