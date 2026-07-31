---
id: KN-LIT-6203
type: literature
title: "Related-key Attacks Against Full Hummingbird-2"
authors:
  - "Markku-Juhani O. Saarinen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present attacks on full Hummingbird-2 which are able to recover the 128-bit secret keys of two black box cipher instances that have a certain type of low-weight XOR difference in their keys. We call these highly correlated keys as they produce the same ciphertext with a significant probability.

## Key claims (as reported)
- The complexity of our main chosen-IV key-recovery attack is 264 .
- The first 64 bits of the key can be independently recovered with only 236 effort.
- This is the first sub-exhaustive attack on the full cipher under two related keys.
- Our attacks use some novel tricks and techniques which are made possible by Hummingbird-2’s unique word-based structure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240436 (1).pdf`
- `downloads/84240436 (2).pdf`
- `downloads/84240436 (3).pdf`
- `downloads/84240436.pdf`
