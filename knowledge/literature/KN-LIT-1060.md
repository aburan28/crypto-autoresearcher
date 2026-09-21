---
id: KN-LIT-1060
type: literature
title: "A note on “a multi-instance cancelable fingerprint biometric based secure session key agreement protocol employing elliptic curve"
authors:
  - "Zhengjun Cao"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/993"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/993"
tags: [elliptic-curve, hash, protocol, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that the key agreement scheme [Multim. 80:799-829, 2021] is flawed.

## Key claims (as reported)
- (1) The scheme is a hybrid which piles up various tools such as public key encryption, signature, symmetric key encryption, hash function, cancelable templates from thumb fingerprints, and elliptic curve cryptography.
- These tools are excessively used because key agreement is just a simple cryptographic primitive in contrast to public key encryption.
- (2) The involved reliance is very intricate.
- Especially, the requirement for a secure channel between two parties is generally unavailable.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-993.pdf`
