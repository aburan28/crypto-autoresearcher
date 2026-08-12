---
id: KN-LIT-6858
type: literature
title: "Sub-Linear, Secure Comparison With Two Non-Colluding Parties"
authors:
  - "Tomas Toft"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The classic problem in the field of secure computation is Yao’s millionaires’ problem; we consider two new protocols solving a variation of this: a number of parties, P1 , . . . , Pn , securely hold two `bit values, x and y – e.g. x and y could be encrypted or secret shared. They wish to obtain a bit stating whether x is greater than y using only secure arithmetic; this should be done without revealing any information, even the output should remain secret.

## Key claims (as reported)
- The present setting is special in the sense that it is assumed that two specific parties, referred to as Alice and Bob, are non-colluding.
- Though this assumption is not satisfied in general, it clearly is for the main example of this work: two-party computation based on Paillier encryption.
- The first solution requires O(log(`)(κ + loglog(`))) secure arithmetic operations in O(log(`)) rounds, where κ is a correctness parameter.
- The second solution requires only a constant number of rounds, but increases √ complexity to O( `(κ + log(`))) arithmetic operations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65710181 (1).pdf`
- `downloads/65710181 (2).pdf`
- `downloads/65710181 (3).pdf`
- `downloads/65710181.pdf`
