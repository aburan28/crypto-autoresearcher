---
id: KN-LIT-1643
type: literature
title: "Explicit cost analysis of Toom-4 multiplication for incomplete NTT in lattice-based cryptography"
authors:
  - "Sakura Oku"
  - "Momonari Kudo"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/971"
  doi: null
  arxiv: "2605.17505"
  url: "https://eprint.iacr.org/2026/971"
tags: [lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Polynomial multiplication is fundamental in lattice-based cryptography. While the Number Theoretic Transform (NTT) enables fast multiplication, it imposes constraints on the modulus of the coefficient field.

## Key claims (as reported)
- (2025) addressed this limitation by analyzing the incomplete NTT, which combines a truncated NTT with conventional multiplication methods.
- In this work, we revisit Toom-4 multiplication in the context of incomplete NTT.
- Although Toom-4 is asymptotically faster than Karatsuba, its precise cost has not been expressed in a form compatible with the incomplete NTT framework.
- We present a concrete Toom-4 implementation and derive explicit operation counts that separate additions/subtractions and multiplications over the coefficient field.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-971.pdf`
- `downloads/2605.17505v1.pdf`
