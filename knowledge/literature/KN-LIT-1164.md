---
id: KN-LIT-1164
type: literature
title: "Revocable Cryptography from Learning with Errors"
authors:
  - "Prabhanjan Ananth⋆⋆"
  - "Alexander Poremba⋆ ⋆ ⋆"
  - "Vinod Vaikuntanathan"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/325"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/325"
tags: [fhe, lattice, pairing, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Quantum cryptography leverages unique properties of quantum information in order to construct cryptographic primitives that are oftentimes impossible classically. In this work, we build on the no-cloning principle of quantum mechanics and design cryptographic schemes with key revocation capabilities.

## Key claims (as reported)
- We consider schemes where secret keys are represented as quantum states with the guarantee that, once the secret key is successfully revoked from a user, they no longer have the ability to perform the same functionality as before.
- We define and construct several fundamental cryptographic primitives with key-revocation capabilities, namely pseudorandom functions, secretkey and public-key encryption, and even fully homomorphic encryption, assuming the quantum sub-exponential hardness of the learning with errors problem.
- Central to all our constructions is our method of making the Dual-Regev encryption (Gentry, Peikert and Vaikuntanathan, STOC 2008) scheme revocable.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369168 (1).pdf`
- `downloads/14369168.pdf`
