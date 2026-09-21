---
id: KN-LIT-6482
type: literature
title: "Securing RSA-KEM via the AES"
authors:
  - "J. Jonsson"
  - "M.J.B. Robshaw"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, provable-security, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
RSA-KEM is a popular key encapsulation mechanism that combines the RSA trapdoor permutation with a key derivation function (KDF). Often the details of the KDF are viewed as orthogonal to the RSA-KEM construction and the RSA-KEM proof of security models the KDF as a random oracle.

## Key claims (as reported)
- In this paper we present an AES-based KDF that has been explicitly designed so that we can appeal to currently held views on the ideal behaviour of the AES when proving the security of RSA-KEM.
- Thus, assuming that encryption with the AES provides a permutation of 128-bit input blocks that is chosen uniformily at random for each key k, the security of RSA-KEM against chosen-ciphertext attacks can be related to the hardness of inverting RSA.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33860030 (1).pdf`
- `downloads/33860030 (2).pdf`
- `downloads/33860030 (3).pdf`
- `downloads/33860030.pdf`
