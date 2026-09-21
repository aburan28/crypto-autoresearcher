---
id: KN-LIT-4160
type: literature
title: "Hardness Preserving Reductions via Cuckoo Hashing"
authors:
  - "Itay Berman⋆"
  - "Iftach Haitner⋆"
  - "Ilan Komargodaki⋆⋆"
  - "Moni Naor⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A common method for increasing the usability and uplifting the security of pseudorandom function families (PRFs) is to “hash” the inputs into a smaller domain before applying the PRF. This approach, known as “Levin’s trick”, is used to achieve “PRF domain extension” (using a short, e.g., fixed, input length PRF to get a variable-length PRF), and more recently to transform non-adaptive PRFs to adaptive ones. √ Such reductions, however, are vulnerable to a “birthday attack”: after |U| queries to the resulting PRF, where U being the hash function range, a collision (i.e., two distinct inputs have the same hash value) happens with high probability.

## Key claims (as reported)
- As a consequence, the resulting PRF is insecure against an attacker making this number of queries.
- In this work we show how to go beyond the birthday attack barrier, by replacing the above simple hashing approach with a variant of cuckoo hashing — a hashing paradigm typically used for resolving hash collisions in a table, by using two hash functions and two tables, and cleverly assigning each element into one of the two tables.
- We use this approach to obtain: (i) A domain extension method that requires just two calls to the original PRF, can withstand as many queries as the original domain size and has a distinguishing probability that is exponentially small in the non cryptographic work.
- (ii) A security-preserving reduction from non-adaptive to adaptive PRFs.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850040 (1).pdf`
- `downloads/77850040 (2).pdf`
- `downloads/77850040 (3).pdf`
- `downloads/77850040.pdf`
