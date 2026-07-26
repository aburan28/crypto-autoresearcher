---
id: KN-LIT-3241
type: literature
title: "Cryptanalysis of HMAC/NMAC-Whirlpool"
authors:
  - "Jian Guo"
  - "Yu Sasaki"
  - "Lei Wang"
  - "Shuang Wu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we present universal forgery and key recovery attacks on the most popular hash-based MAC constructions, e.g., HMAC and NMAC, instantiated with an AES-like hash function Whirlpool. These attacks work with Whirlpool reduced to 6 out of 10 rounds in single-key setting.

## Key claims (as reported)
- To the best of our knowledge, this is the first result on “original” key recovery for HMAC (previous works only succeeded in recovering the equivalent keys).
- Interestingly, the number of attacked rounds is comparable with that for collision and preimage attacks on Whirlpool hash function itself.
- Lastly, we present a distinguishing-H attack against the full HMAC- and NMAC-Whirlpool.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700021 (1).pdf`
- `downloads/82700021 (2).pdf`
- `downloads/82700021 (3).pdf`
- `downloads/82700021.pdf`
