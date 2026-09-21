---
id: KN-LIT-4937
type: literature
title: "Mitigating Dictionary Attacks on Password-Protected Local Storage"
authors:
  - "Ran Canetti"
  - "Shai Halevi"
  - "Michael Steiner"
year: null
venue: null
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
We address the issue of encrypting data in local storage using a key that is derived from the user’s password. The typical solution in use today is to derive the key from the password using a cryptographic hash function.

## Key claims (as reported)
- This solution provides relatively weak protection, since an attacker that gets hold of the encrypted data can mount an off-line dictionary attack on the user’s password, thereby recovering the key and decrypting the stored data.
- We propose an approach for limiting off-line dictionary attacks in this setting without relying on secret storage or secure hardware.
- In our proposal, the process of deriving a key from the password requires the user to solve a puzzle that is presumed to be solvable only by humans (e.g, a CAPTCHA).
- We describe a simple protocol using this approach: many different puzzles are stored on the disk, the user’s password is used to specify which of them need to be solved, and the encryption key is derived from the password and the solutions of the specified puzzles.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170158 (1).pdf`
- `downloads/41170158 (2).pdf`
- `downloads/41170158 (3).pdf`
- `downloads/41170158.pdf`
