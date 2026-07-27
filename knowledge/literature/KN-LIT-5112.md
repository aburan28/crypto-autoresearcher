---
id: KN-LIT-5112
type: literature
title: "New Distinguishing Attack on MAC using Secret-Prefix Method"
authors:
  - "Xiaoyun Wang"
  - "Wei Wang"
  - "Keting Jia"
  - "Meiqin Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pollard-rho, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a new distinguisher which can be applied to secret-prefix MACs with the message length prepended to the message before hashing. The new distinguisher makes use of a special truncated differential path with high probability to distinguish an inner near-collision in the first round.

## Key claims (as reported)
- Once the inner near-collision is detected, we can recognize an instantiated MAC from a MAC with a random function.
- The complexity for distinguishing the MAC with 43-step reduced SHA-1 is 2124.5 queries.
- For the MAC with 61-step SHA-1, the complexity is 2154.5 queries.
- The success probability is 0.70 for both.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56650374 (1).pdf`
- `downloads/56650374 (2).pdf`
- `downloads/56650374 (3).pdf`
- `downloads/56650374.pdf`
