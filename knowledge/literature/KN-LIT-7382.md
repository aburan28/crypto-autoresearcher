---
id: KN-LIT-7382
type: literature
title: "Universal Designated Verifier Signature Proof (or How to Efficiently Prove Knowledge of a Signature)"
authors:
  - "Joonsang Baek"
  - "Reihaneh Safavi-Naini"
  - "Willy Susilo"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Proving knowledge of a signature has many interesting applications. As one of them, the Universal Designated Verifier Signature (UDVS), introduced by Steinfeld et al. in Asiacrypt 2003 aims to protect a signature holder’s privacy by allowing him to convince a verifier that he holds a valid signature from the signer without revealing the signature itself.

## Key claims (as reported)
- The essence of the UDVS is a transformation from a publicly verifiable signature to a designated verifier signature, which is performed by the signature holder who does not have access to the signer’s secret key.
- However, one significant inconvenience of all the previous UDVS schemes considered in the literature is that they require the designated verifier to create a public key using the signer’s public key parameter and have it certified to ensure the resulting public key is compatible with the setting that the signer provided.
- This restriction is unrealistic in several situations where the verifier is not willing to go through such setup process.
- In this paper, we resolve this problem by introducing a new type of UDVS.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/641 (1).pdf`
- `downloads/641 (2).pdf`
- `downloads/641 (3).pdf`
- `downloads/641.pdf`
