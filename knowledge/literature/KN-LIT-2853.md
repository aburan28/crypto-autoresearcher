---
id: KN-LIT-2853
type: literature
title: "CCA-Secure Proxy Re-Encryption without Pairings?"
authors:
  - "Jun Shao"
  - "Zhenfu Cao"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a proxy re-encryption scheme, a semi-trusted proxy can transform a ciphertext under Alice’s public key into another ciphertext that Bob can decrypt. However, the proxy cannot access the plaintext.

## Key claims (as reported)
- Due to its transformation property, proxy re-encryption can be used in many applications, such as encrypted email forwarding.
- In this paper, by using signature of knowledge and Fijisaki-Okamoto conversion, we propose a proxy re-encryption scheme without pairings, in which the proxy can only transform the ciphertext in one direction.
- The proposal is secure against chosen ciphertext attack (CCA) and collusion attack in the random oracle model based on Decisional Diffie-Hellman (DDH) assumption over Z∗N 2 and integer factorization assumption, respectively.
- To the best of our knowledge, it is the first unidirectional PRE scheme with CCA security and collusion-resistance.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430361 (1).pdf`
- `downloads/54430361 (2).pdf`
- `downloads/54430361 (3).pdf`
- `downloads/54430361.pdf`
