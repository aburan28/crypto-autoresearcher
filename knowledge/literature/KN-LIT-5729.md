---
id: KN-LIT-5729
type: literature
title: "Partial Key Exposure Attack on Short Secret Exponent CRT-RSA"
authors:
  - "Alexander May"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let (N, e) be an RSA public key, where N = pq is the product of equal bitsize primes p, q. Let dp , dq be the corresponding secret CRT-RSA exponents.

## Key claims (as reported)
- Using a Coppersmith-type attack, Takayasu, Lu and Peng (TLP) recently showed that one obtains the factorization of N in polynomial time, provided that dp , dq ≤ N 0.122 .
- Building on the TLP attack, we show the first Partial Key Exposure attack on short secret exponent CRT-RSA.
- Namely, let N 0.122 ≤ dp , dq ≤ N 0.5 .
- Then we show that a constant known fraction of the least significant bits (LSBs) of both dp , dq suffices to factor N in polynomial time.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900029 (1).pdf`
- `downloads/130900029.pdf`
