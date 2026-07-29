---
id: KN-LIT-1357
type: literature
title: "Compact, Efficient and CCA-Secure Updatable Encryption from Isogenies"
authors:
  - "Antonin Leroux"
  - "Maxime Roméas"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1853"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1853"
tags: [elliptic-curve, isogeny, lattice, pqc, provable-security, quantum, sidh-csidh]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Updatable Encryption (UE) allows ciphertexts to be updated under new keys without decryption, enabling efficient key rotation. Constructing post-quantum UE with strong security guarantees is challenging: the only known CCA-secure scheme, COM-UE, uses bitwise encryption, resulting in large ciphertexts and high computational costs.

## Key claims (as reported)
- We introduce DINE, a CCA-secure, isogeny-based post-quantum UE scheme that is both compact and efficient.
- Each encryption, decryption, or update requires only a few power-of-2 isogeny computations in dimension 2 to encrypt 28B messages, yielding 320B ciphertexts and 896B update tokens at NIST security level 1—significantly smaller than prior constructions.
- Our full C implementation demonstrates practical performances: updates in 28ms, encryptions in 48ms, and decryptions in 86ms.
- Our design builds on recent advances in isogeny-based cryptography, combining high-dimensional isogeny representations with the Deuring correspondence.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1853.pdf`
