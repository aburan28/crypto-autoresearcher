---
id: KN-LIT-3447
type: literature
title: "Distinguisher and Related-Key Attack on the Full AES-256"
authors:
  - "Alex Biryukov"
  - "Dmitry Khovratovich"
  - "Ivica Nikolić"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we construct a chosen-key distinguisher and a related-key attack on the full 256-bit key AES. We define a notion of differential q-multicollision and show that for AES-256 q-multicollisions can be constructed in time q · 267 and with negligible memory, while we prove that the same task for an ideal cipher of the same block size q−1 128 would require at least O(q · 2 q+1 ) time.

## Key claims (as reported)
- Using similar approach and with the same complexity we can also construct q-pseudo collisions for AES-256 in Davies-Meyer mode, a scheme which is provably secure in the ideal-cipher model.
- We have also computed partial q-multicollisions in time q · 237 on a PC to verify our results.
- These results show that AES-256 can not model an ideal cipher in theoretical constructions.
- Finally we extend our results to find the first publicly known attack on the full 14-round AES-256: a related-key distinguisher which works for one out of every 235 keys with 2120 data and time complexity and negligible memory.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770229 (1).pdf`
- `downloads/56770229 (2).pdf`
- `downloads/56770229 (3).pdf`
- `downloads/56770229.pdf`
