---
id: KN-LIT-2065
type: literature
title: "A Generalized Wiener Attack on RSA"
authors:
  - "Johannes Blömer"
  - "Alexander May"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an extension of Wiener’s attack on small RSA secret decryption exponents [10]. Wiener showed that every RSA public key tuple (N, e) with e ∈ ∗φ(N ) that satisfies ed − 1 = 0 mod φ(N ) for 1 some d < 13 N 4 yields the factorization of N = pq.

## Key claims (as reported)
- Our new method finds p and q in polynomial time for every (N, e) satisfying ex + y = 0 mod φ(N ) with x< 1 14 N 3 and 3 |y| = O(N − 4 ex).
- In other words, the generalization works for all secret keys d = −xy −1 , where x, y are suitably small.
- We show that the number of these weak 3 keys is at least N 4 − and that the number increases with decreasing prime difference p − q.
- As an application of our new attack, we present the cryptanalysis of an RSA-type scheme presented by Yen, Kim, Lim and Moon [11, 12].

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/29470001 (1).pdf`
- `downloads/29470001 (2).pdf`
- `downloads/29470001.pdf`
