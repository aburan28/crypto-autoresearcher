---
id: KN-LIT-1963
type: literature
title: "Zero-shot deep-unfolding decoder for QC-MDPC McEliece cryptosystems"
authors:
  - "Shingo Kukita"
  - "Rei Iseki"
  - "Takeshi Namatame"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/982"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/982"
tags: [cryptanalysis, factoring, lattice, pqc, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Keywords: Code-based cryptography · QC-MDPC McEliece cryptosystem · Deep learning. The QC-MDPC McEliece cryptosystem is a promising candidate for post-quantum cryptography, and the decoding performance of the underlying QC-MDPC code directly affects the security of the scheme.

## Key claims (as reported)
- Deep unfolding, a framework that unfolds an iterative algorithm into a neural network with trainable weights, has been shown to improve belief propagation (BP) decoding for codes with dense parity-check matrices.
- However, applying deep unfolding directly to the large QC-MDPC codes used in practice is impractical owing to the computational cost of training.
- Moreover, in QC-MDPC-based cryptosystems, the parity-check matrix serves as the secret key and must be replaced periodically; key-specific training would therefore need to be repeated at each replacement.
- We address both issues through zero-shot transfer.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-982.pdf`
