---
id: KN-LIT-3521
type: literature
title: "Efficient and Provably Secure Methods for Switching from Arithmetic to Boolean Masking Blandine Debraize"
authors:
  - "rue de la Verrerie"
  - "Meudon Cedex"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A large number of secret key cryptographic algorithms combine Boolean and arithmetic instructions. To protect such algorithms against first order side channel analysis, it is necessary to perform conversions between Boolean masking and arithmetic masking.

## Key claims (as reported)
- Louis Goubin proposed in [7] an efficient method to convert from Boolean to arithmetic masking.
- However the conversion method he also proposed in [7] to switch from arithmetic to Boolean is less efficient and could be a bottleneck in some implementations.
- Two faster methods were proposed in [3] and [11], both using precomputed tables.
- We show in this paper that the algorithm in [3] is bugged, and propose an efficient correction.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74280103 (1).pdf`
- `downloads/74280103 (2).pdf`
- `downloads/74280103 (3).pdf`
- `downloads/74280103.pdf`
