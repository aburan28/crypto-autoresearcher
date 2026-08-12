---
id: KN-LIT-6456
type: literature
title: "Secure Obfuscation for Encrypted Signatures"
authors:
  - "Satoshi Hada"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Obfuscation is one of the most intriguing open problems in cryptography and only a few positive results are known. In TCC’07, Hohenberger et al. proposed an obfuscator for a re-encryption functionality, which takes a ciphertext for a message encrypted under Alice’s public key and transforms it into a ciphertext for the same message under Bob’s public key [24].

## Key claims (as reported)
- It is the first complicated cryptographic functionality that can be securely obfuscated, but obfuscators for such cryptographic functionalities are still elusive.
- In this paper, we consider obfuscation for encrypted signature (ES) functionalities, which generate a signature on a given message under Alice’s secret signing key and encrypt the signature under Bob’s public encryption key.
- We propose a special ES functionality, which is the sequential composition of Waters’s signature scheme [33] and the linear encryption scheme proposed by Boneh, Boyen, and Shacham [5], and construct a secure obfuscator for it.
- We follow the security argument by Hohenberger et al. to prove that our proposed obfuscator satisfies a virtual black-box property (VBP), which guarantees that the security of the signature scheme is preserved even when adversaries are given an obfuscated program.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320116 (1).pdf`
- `downloads/66320116 (2).pdf`
- `downloads/66320116 (3).pdf`
- `downloads/66320116.pdf`
