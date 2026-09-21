---
id: KN-LIT-6495
type: literature
title: "Security Analysis of PRINCE"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this article, we provide the first third-party security analysis of the PRINCE lightweight block cipher, and the underlying PRINCEcore . First, while no claim was made by the authors regarding related-key attacks, we show that one can attack the full cipher with only a single pair of related keys, and then reuse the same idea to derive an attack in the single-key model for the full PRINCEcore for several instances of the α parameter (yet not the one randomly chosen by the designers).

## Key claims (as reported)
- We also show how to exploit the structural linear relations that exist for PRINCE in order to obtain a key recovery attack that slightly breaks the security claims for the full cipher.
- We analyze the application of integral attacks to get the best known key-recovery attack on a reduced version of the PRINCE cipher.
- Finally, we provide time-memory-data tradeoffs that require only known plaintext-ciphertext data and that can be applied to full PRINCE.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240085 (1).pdf`
- `downloads/84240085 (2).pdf`
- `downloads/84240085 (3).pdf`
- `downloads/84240085.pdf`
