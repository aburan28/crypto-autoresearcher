---
id: KN-LIT-6205
type: literature
title: "Related-Key Forgeries for Prøst-OTR"
authors:
  - "Christoph Dobraunig"
  - "Maria Eichlseder"
  - "Florian Mendel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a forgery attack on Prøst-OTR in a related-key setting. Prøst is a family of authenticated encryption algorithms proposed as candidates in the currently ongoing CAESAR competition, and Prøst-OTR is one of the three variants of the Prøst design.

## Key claims (as reported)
- The attack exploits how the Prøst permutation is used in an Even-Mansour construction in the Feistel-based OTR mode of operation.
- Given the ciphertext and tag for any two messages under two related keys K and K ⊕ ∆ with related nonces, we can forge the ciphertext and tag for a modified message under K.
- If we can query ciphertexts for chosen messages under K ⊕ ∆, we can achieve almost universal forgery for K.
- The computational complexity is negligible.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400153 (4).pdf`
- `downloads/85400153 (5).pdf`
