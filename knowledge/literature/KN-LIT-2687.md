---
id: KN-LIT-2687
type: literature
title: "Beyond 2c/2 Security in Sponge-Based Authenticated Encryption Modes"
authors:
  - "Philipp Jovanovic"
  - "Atul Luykx"
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Sponge function is known to achieve 2c/2 security, where c is its capacity. This bound was carried over to keyed variants of the function, such as SpongeWrap, to achieve a min{2c/2 , 2κ } security bound, with κ the key length.

## Key claims (as reported)
- Similarly, many CAESAR competition submissions are designed to comply with the classical 2c/2 security bound.
- We show that Sponge-based constructions for authenticated encryption can achieve the significantly higher bound of min{2b/2 , 2c , 2κ } asymptotically, with b > c the permutation size, by proving that the CAESAR submission NORX achieves this bound.
- Furthermore, we show how to apply the proof to five other Sponge-based CAESAR submissions: Ascon, CBEAM/STRIBOB, ICEPOLE, Keyak, and two out of the three PRIMATEs.
- A direct application of the result shows that the parameter choices of these submissions are overly conservative.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730246 (1).pdf`
- `downloads/88730246 (2).pdf`
- `downloads/88730246 (3).pdf`
- `downloads/88730246.pdf`
