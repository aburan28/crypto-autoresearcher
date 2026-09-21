---
id: KN-LIT-4562
type: literature
title: "Jammin’ on the deck"
authors:
  - "Norica Bcuiei"
  - "Joan Daemen"
  - "Seth Hoffert"
  - "Gilles Van Assche"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, mov-fr, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Currently, a vast majority of symmetric-key cryptographic schemes are built as block cipher modes. The block cipher is designed to be hard to distinguish from a random permutation and this is supported by cryptanalysis, while (good) modes can be proven secure if a random permutation takes the place of the block cipher.

## Key claims (as reported)
- As such, block ciphers form an abstraction level that marks the border between cryptanalysis and security proofs.
- In this paper, we investigate a re-factored version of symmetric-key cryptography built not around the block ciphers but rather the deck function: a keyed function with arbitrary input and output length and incrementality properties.
- This allows for modes of use that are simpler to analyze and still very efficient thanks to the excellent performance of currently proposed deck functions.
- We focus on authenticated encryption (AE) modes with varying levels of robustness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910040 (1).pdf`
- `downloads/137910040.pdf`
