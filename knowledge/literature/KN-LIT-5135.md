---
id: KN-LIT-5135
type: literature
title: "New Preimage Attacks Against Reduced SHA-1"
authors:
  - "Simon Knellwolf⋆"
  - "Dmitry Khovratovich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper shows preimage attacks against reduced SHA-1 up to 57 steps. The best previous attack has been presented at CRYPTO 2009 and was for 48 steps finding a two-block preimage with incorrect padding at the cost of 2159.3 evaluations of the compression function.

## Key claims (as reported)
- For the same variant our attacks find a one-block preimage at 2150.6 and a correctly padded two-block preimage at 2151.1 evaluations of the compression function.
- The improved results come out of a differential view on the meet-in-the-middle technique originally developed by Aoki and Sasaki.
- The new framework closely relates meet-in-the-middle attacks to differential cryptanalysis which turns out to be particularly useful for hash functions with linear message expansion and weak diffusion properties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170366 (1).pdf`
- `downloads/74170366 (2).pdf`
- `downloads/74170366 (3).pdf`
- `downloads/74170366 (4).pdf`
- `downloads/74170366 (5).pdf`
- `downloads/74170366.pdf`
