---
id: KN-LIT-3414
type: literature
title: "Differential and Linear Cryptanalysis of a Reduced-Round SC2000"
authors:
  - "Hitoshi Yanami"
  - "Takeshi Shimoyama"
  - "Orr Dunkelman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We analyze the security of the SC2000 block cipher against both differential and linear attacks. SC2000 is a six-and-a-half-round block cipher, which has a unique structure that includes both the Feistel and Substitution-Permutation Network (SPN) structures.

## Key claims (as reported)
- Taking the structure of SC2000 into account, we investigate one- and two-round iterative differential and linear characteristics.
- We present two-round iterative differential characteristics with probability 2−58 and two-round iterative linear characteristics with probability 2−56 .
- These characteristics, which we obtained through a search, allowed us to attack four-anda-half-round SC2000 in the 128-bit user-key case.
- Our differential attack needs 2103 pairs of chosen plaintexts and 220 memory accesses and our linear attack needs 2115.17 known plaintexts and 242.32 memory accesses, or 2104.32 known plaintexts and 283.32 memory accesses.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/23650035 (1).pdf`
- `downloads/23650035 (2).pdf`
- `downloads/23650035.pdf`
