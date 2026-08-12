---
id: KN-LIT-4217
type: literature
title: "Higher-Order Side Channel Security and Mask Refreshing"
authors:
  - "Thomas Roche"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking is a widely used countermeasure to protect block cipher implementations against side-channel attacks. The principle is to split every sensitive intermediate variable occurring in the computation into d + 1 shares, where d is called the masking order and plays the role of a security parameter.

## Key claims (as reported)
- A masked implementation is then said to achieve dth -order security if any set of d (or less) intermediate variables does not reveal key-dependent information.
- At CHES 2010, Rivain and Prouff have proposed a higher-order masking scheme for AES that works for any arbitrary order d.
- This scheme, and its subsequent extensions, are based on an improved version of the shared multiplication processing published by Ishai et al. at CRYPTO 2003.
- This improvement enables better memory/timing performances but its security relies on the refreshing of the masks at some points in the algorithm.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240382 (1).pdf`
- `downloads/84240382 (2).pdf`
- `downloads/84240382 (3).pdf`
- `downloads/84240382.pdf`
