---
id: KN-LIT-3423
type: literature
title: "Differential Meet-In-The-Middle Cryptanalysis"
authors:
  - "Christina Boura"
  - "Nicolas David"
  - "Patrick Derbez"
  - "Gregor Leander"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we introduce the differential meet-in-the-middle framework, a new cryptanalysis technique for symmetric primitives. Our new cryptanalysis method combines techniques from both meet-in-themiddle and differential cryptanalysis.

## Key claims (as reported)
- As such, the introduced technique can be seen as a way of extending meet-in-the-middle attacks and their variants but also as a new way to perform the key recovery part in differential attacks.
- We apply our approach to SKINNY-128-384 in the single-key model and to AES-256 in the related-key model.
- Our attack on SKINNY-128-384 permits to break 25 out of the 56 rounds of this variant and improves by two rounds the previous best known attacks.
- For AES-256 we attack 12 rounds by considering two related keys, thus outperforming the previous best related-key attack on AES-256 with only two related keys by 2 rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850336 (1).pdf`
- `downloads/140850336.pdf`
