---
id: KN-LIT-4460
type: literature
title: "Improving the Generalized Feistel"
authors:
  - "Tomoyasu Suzaki"
  - "Kazuhiko Minematsu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The generalized Feistel structure (GFS) is a generalized form of the classical Feistel cipher. A popular version of GFS, called TypeII, divides a message into k > 2 sub blocks and applies a (classical) Feistel transformation for every two sub blocks, and then performs a cyclic shift of k sub blocks.

## Key claims (as reported)
- Type-II GFS has many desirable features for implementation.
- A drawback, however, is its low diffusion property with a large k.
- This weakness can be exploited by some attacks, such as impossible differential attack.
- To protect from them, Type-II GFS generally needs a large number of rounds.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470020 (1).pdf`
- `downloads/61470020 (2).pdf`
- `downloads/61470020 (3).pdf`
- `downloads/61470020.pdf`
