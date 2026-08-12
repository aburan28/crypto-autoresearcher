---
id: KN-LIT-7204
type: literature
title: "Towards Black-Box Accountable Authority IBE with Short Ciphertexts and Private Keys"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Crypto’07, Goyal introduced the concept of Accountable Authority Identity-Based Encryption as a convenient tool to reduce the amount of trust in authorities in Identity-Based Encryption. In this model, if the Private Key Generator (PKG) maliciously re-distributes users’ decryption keys, it runs the risk of being caught and prosecuted.

## Key claims (as reported)
- Goyal proposed two constructions: the first one is efficient but can only trace well-formed decryption keys to their source; the second one allows tracing obfuscated decryption boxes in a model (called weak black-box model) where cheating authorities have no decryption oracle.
- The latter scheme is unfortunately far less efficient in terms of decryption cost and ciphertext size.
- In this work, we propose a new construction that combines the efficiency of Goyal’s first proposal with a very simple weak black-box tracing mechanism.
- Our scheme is described in the selective-ID model but readily extends to meet all security properties in the adaptiveID sense, which is not known to be true for prior black-box schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430241 (1).pdf`
- `downloads/54430241 (2).pdf`
- `downloads/54430241 (3).pdf`
- `downloads/54430241.pdf`
