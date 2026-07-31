---
id: KN-LIT-2722
type: literature
title: "Black-Box Analysis of the Block-Cipher-Based Hash-Function Constructions from PGV"
authors:
  - "John Black"
  - "Phillip Rogaway"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Preneel, Govaerts, and Vandewalle [?] considered the 64 most basic ways to construct a hash function H: {0, 1}∗ → {0, 1}n from a block cipher E: {0, 1}n × {0, 1}n → {0, 1}n . They regarded 12 of these 64 schemes as secure, though no proofs or formal claims were given.

## Key claims (as reported)
- The remaining 52 schemes were shown to be subject to various attacks.
- Here we provide a formal and quantitative treatment of the 64 constructions considered by PGV.
- We prove that, in a black-box model, the 12 schemes that PGV singled out as secure really are secure: we give tight upper and lower bounds on their collision resistance.
- Furthermore, by stepping outside of the Merkle-Damgård approach to analysis, we show that an additional 8 of the 64 schemes are just as collision resistant (up to a small constant) as the first group of schemes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420321 (1).pdf`
- `downloads/24420321 (2).pdf`
- `downloads/24420321.pdf`
