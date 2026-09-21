---
id: KN-LIT-679
type: literature
title: "Implementing Grover oracles for quantum key search on AES and LowMC"
authors:
  - "Samuel Jaques∗"
  - "Michael Naehrig"
  - "Martin Roetteler"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/1146"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/1146"
tags: [binary-field, cryptanalysis, dlp, ecdsa, hash, pqc, provable-security, quantum, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Grover’s search algorithm gives a quantum attack against block ciphers by searching for a key that matches a small number of √ plaintext-ciphertext pairs. This attack uses O( N ) calls to the cipher to search a key space of size N .

## Key claims (as reported)
- Previous work in the specific case of AES derived the full gate cost by analyzing quantum circuits for the cipher, but focused on minimizing the number of qubits.
- In contrast, we study the cost of quantum key search attacks under a depth restriction and introduce techniques that reduce the oracle depth, even if it requires more qubits.
- As cases in point, we design quantum circuits for the block ciphers AES and LowMC.
- Our circuits give a lower overall attack cost in both the gate count and depth-times-width cost models.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105182 (1).pdf`
- `downloads/12105182.pdf`
- `downloads/2019-1146.pdf`
