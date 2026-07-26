---
id: KN-LIT-5496
type: literature
title: "On the Impossibility of Efficiently Combining Collision Resistant Hash Functions"
authors:
  - "Dan Boneh"
  - "Xavier Boyen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mpc, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let H1 , H2 be two hash functions. We wish to construct a new hash function H that is collision resistant if at least one of H1 or H2 is collision resistant.

## Key claims (as reported)
- Concatenating the output of H1 and H2 clearly works, but at the cost of doubling the hash output size.
- We ask whether a better construction exists, namely, can we hedge our bets without doubling the size of the output?
- We take a step towards answering this question in the negative — we show that any secure construction that evaluates each hash function once cannot output fewer bits than simply concatenating the given functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170565 (1).pdf`
- `downloads/41170565 (2).pdf`
- `downloads/41170565 (3).pdf`
- `downloads/41170565.pdf`
