---
id: KN-LIT-4434
type: literature
title: "Improved Security for OCB3"
authors:
  - "Ritam Bhaumik"
  - "Mridul Nandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
OCB3 is the current version of the OCB authenticated encryption mode which is selected for the third round in CAESAR. So far the integrity analysis has limited to an adversary making a single forging attempt.

## Key claims (as reported)
- A simple extension for the best known bound establishes integrity security as long as the total number of query blocks (including encryptions and forging attempts) does not exceed the birthday-bound.
- In this paper we show an improved bound for integrity of OCB3 in terms of the number of blocks in the forging attempt.
- In particular we show that when the number of encryption query blocks is not more than birthdaybound (an assumption without which the privacy guarantee of OCB3 disappears), even an adversary making forging attempts with the number of blocks in the order of 2n /`MAX (n being the block-size and `MAX being the length of the longest block) may fail to break the integrity of OCB3.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240325 (1).pdf`
- `downloads/106240325.pdf`
