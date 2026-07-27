---
id: KN-LIT-3308
type: literature
title: "Cryptographic Pseudorandom Generators Can"
authors:
  - "Make Cryptosystems Problematic"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Randomness is an essential resource for cryptography. For practical randomness generation, the security notion of pseudorandom generators (PRGs) intends to automatically preserve (computational) security of cryptosystems when used in implementation.

## Key claims (as reported)
- Nevertheless, some opposite case such as in computational randomness extractors (Barak et al., CRYPTO 2011) is known (but not yet systematically studied so far) where the security can be lost even by applying secure PRGs.
- The present paper aims at pushing ahead the observation and understanding about such a phenomenon; we reveal such situations at layers of primitives and protocols as well, not just of building blocks like randomness extractors.
- We present three typical types of such cases: (1) adversaries can legally see the seed of the PRGs (including the case of randomness extractors); (2) the set of “bad” randomness may be not efficiently recognizable; (3) the formulation of a desired property implicitly involves non-uniform distinguishers for PRGs.
- We point out that the semi-honest security of multiparty computation also belongs to Type 1, while the correctness with negligible decryption error probability for public key encryption belongs to Types 2 and 3.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110193 (1).pdf`
- `downloads/127110193.pdf`
