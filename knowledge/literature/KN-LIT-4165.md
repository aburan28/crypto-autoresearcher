---
id: KN-LIT-4165
type: literature
title: "Hash Function Balance and its Impact on Birthday Attacks"
authors:
  - "Mihir Bellare"
  - "Tadayoshi Kohno"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Textbooks tell us that a birthday attack on a hash function h with range size r requires r1/2 trials (hash computations) to find a collision. But this is quite misleading, being true only if h is regular, meaning all points in the range have the same number of pre-images under h; if h is not regular, fewer trials may be required.

## Key claims (as reported)
- This paper addresses this question by introducing a measure of the “amount of regularity” of a hash function that we call its balance, and then providing estimates of the success-rate of the birthday attack, and the expected number of trials to find a collision, as a function of the balance of the hash function being attacked.
- In particular, we will see that the number of trials can be significantly less than r1/2 for hash functions of low balance.
- This leads us to examine popular design principles, such as the MD (Merkle-Damgård) transform, from the point of view of balance preservation, and to mount experiments to determine the balance of popular hash functions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/bk (1).pdf`
- `downloads/bk (2).pdf`
- `downloads/bk.pdf`
