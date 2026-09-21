---
id: KN-LIT-3224
type: literature
title: "Cryptanalysis of C2"
authors:
  - "Julia Borghoff⋆"
  - "Lars R. Knudsen"
  - "Gregor Leander"
  - "Krystian Matusiewicz⋆"
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
We present several attacks on the block cipher C2, which is used for encrypting DVD Audio discs and Secure Digital cards. C2 has a 56 bit key and a secret 8 to 8 bit S-box.

## Key claims (as reported)
- We show that if the attacker is allowed to choose the key, the S-box can be recovered in 224 C2 encryptions.
- Attacking the 56 bit key for a known S-box can be done in complexity 248 .
- Finally, a C2 implementation with a 8 to 8 bit secret S-box (equivalent to 2048 secret bits) and a 56 bit secret key can be attacked in 253.5 C2 encryptions on average.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770248 (1).pdf`
- `downloads/56770248 (2).pdf`
- `downloads/56770248 (3).pdf`
- `downloads/56770248.pdf`
