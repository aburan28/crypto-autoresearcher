---
id: KN-LIT-7549
type: literature
title: "Zero-Knowledge Arguments for Subverted RSA Groups"
authors:
  - "Dimitris Kolonelos⋆"
  - "Mary Maller"
  - "Mikhail Volkhov⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, cryptanalysis, factoring, fhe, number-theory, pairing, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This work investigates zero-knowledge protocols in subverted RSA groups where the prover can choose the modulus and where the verifier does not know the group order. We introduce a novel technique for extracting the witness from a general homomorphism over a group of unknown order that does not require parallel repetitions.

## Key claims (as reported)
- We then present a NIZK range proof for general homomorphisms as Paillier encryptions in the designated verifier model that works under a subverted setup.
- The key ingredient of our proof is a constant sized NIZK proof of knowledge for a plaintext.
- Security is proven in the ROM assuming an IND-CPA additively homomorphic encryption scheme.
- The verifier’s public key can be maliciously generated and is reusable and linear in the number of proofs to be verified.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940129 (1).pdf`
- `downloads/13940129.pdf`
