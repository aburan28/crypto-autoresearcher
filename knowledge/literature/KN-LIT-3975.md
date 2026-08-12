---
id: KN-LIT-3975
type: literature
title: "Full Key-Recovery Attacks on HMAC/NMAC-MD4 and"
authors:
  - "Pierre-Alain Fouque"
  - "Gaëtan Leurent"
  - "Phong Q. Nguyen"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Crypto ’06, Bellare presented new security proofs for HMAC and NMAC, under the assumption that the underlying compression function is a pseudo-random function family. Conversely, at Asiacrypt ’06, Contini and Yin used collision techniques to obtain forgery and partial key-recovery attacks on HMAC and NMAC instantiated with MD4, MD5, SHA-0 and reduced SHA-1.

## Key claims (as reported)
- In this paper, we present the first full key-recovery attacks on NMAC and HMAC instantiated with a real-life hash function, namely MD4.
- Our main result is an attack on HMAC/NMAC-MD4 which recovers the full MAC secret key after roughly 288 MAC queries and 295 MD4 computations.
- We also extend the partial key-recovery Contini-Yin attack on NMAC-MD5 (in the relatedkey setting) to a full key-recovery attack.
- The attacks are based on generalizations of collision attacks to recover a secret IV, using new differential paths for MD4.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220013 (1).pdf`
- `downloads/46220013 (2).pdf`
- `downloads/46220013 (3).pdf`
- `downloads/46220013.pdf`
