---
id: KN-LIT-2009
type: literature
title: "A Complete and Explicit Security Reduction Algorithm for RSA-based Cryptosystems"
authors:
  - "Kaoru Kurosawa"
  - "Katja Schmidt-Samoa"
  - "Tsuyoshi Takagi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we introduce a conceptually very simple and demonstrative algorithm for finding small solutions (x, y) of ax + y = c mod N , where gcd(a, N ) = 1. Our new algorithm is a variant of the Euclidian algorithm.

## Key claims (as reported)
- Unlike former methods, it finds a small solution whenever such a solution exists.
- Further it runs in time O((log N )3 ), which is the same as the best known previous techniques, e.g. latticebased solutions.
- We then apply our algorithm to RSA-OAEP and RSA-Paillier to obtain better security proofs.
- We believe that there will be many future applications of this algorithm in cryptography.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/28940479 (1).pdf`
- `downloads/28940479 (2).pdf`
- `downloads/28940479.pdf`
