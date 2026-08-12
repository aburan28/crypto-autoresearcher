---
id: KN-LIT-404
type: literature
title: "Parallelizable Rate-1 Authenticated Encryption from Pseudorandom Functions Kazuhiko Minematsu"
authors:
  - "NEC Corporation"
year: 2013
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2013/628"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2013/628"
tags: [hash, pairing, protocol, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes a new scheme for authenticated encryption (AE) which is typically realized as a blockcipher mode of operation. The proposed scheme has attractive features for fast and compact operation.

## Key claims (as reported)
- When it is realized with a blockcipher, it requires one blockcipher call to process one input block (i.e. rate-1), and uses the encryption function of the blockcipher for both encryption and decryption.
- Moreover, the scheme enables one-pass, parallel operation under two-block partition.
- The proposed scheme thus attains similar characteristics as the seminal OCB mode, without using the inverse blockcipher.
- The key idea of our proposal is a novel usage of two-round Feistel permutation, where the round functions are derived from the theory of tweakable blockcipher.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410239 (1).pdf`
- `downloads/84410239 (2).pdf`
- `downloads/84410239 (3).pdf`
- `downloads/84410239.pdf`
