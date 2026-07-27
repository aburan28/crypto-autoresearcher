---
id: KN-LIT-1415
type: literature
title: "Key Recovery Attacks on ZIP Ciphers:"
authors:
  - "Application to ZIP-AES"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/2291"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2291"
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The construction of building beyond-birthday-bound secure pseudorandom functions (PRFs) from the Xor-sum of 2 pseudorandom permutations (PRPs) has been known since EUROCRYPT 1998. However, the first concrete instance was only published recently at FSE 2022: the low-latency PRF Orthros.

## Key claims (as reported)
- Subsequently, at ASIACRYPT 2024, Flórez-Gutiérrez et al. proposed the general framework of ZIP ciphers, where a block cipher E1 ◦ E0 is used to construct the PRF E0 ⊕ E1−1 .
- They propose the PRF ZIP-AES, as the Xor-sum of 5 AES encryption rounds and 5 decryption rounds.
- They discuss differential, linear, and integral distinguishers for this construction, but provide no concrete key recovery attacks.
- Furthermore, they propose ZIP-GIFT as a 64-bit PRF but leave cryptanalysis as future work.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-2291.pdf`
