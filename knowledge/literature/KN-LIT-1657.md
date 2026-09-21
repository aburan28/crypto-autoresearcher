---
id: KN-LIT-1657
type: literature
title: "Finding Random Collisions for Random Degree-2 Functions"
authors:
  - "Xinyu Mao"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1044"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1044"
tags: [hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study distributional collision resistance for random degree-2 functions over prime fields. Let p be a prime and let M h : FN p → Fp , x 7→ (h1 (x), . . . , hM (x)) M < N, be a random polynomial map where each coordinate hi is independently, uniformly chosen at random from all polynomials of degree at most 2 over Fp .

## Key claims (as reported)
- The ideal collision distribution is −1 obtained by choosing x ← FN (h(x)) uniformly at random and output (x, y).
- We p and y ← h give an efficient algorithm whose output distribution is statistically close to this ideal collision distribution whenever pN −M is superpolynomial.
- In other words, we show that random degree2 functions are not distributionally collision-resistant if pN −M is superpolynomial, resolving an open question posed by Bitansky, Haitner, Komargodski, and Yogev (Eurocrypt 2019) in this parameter regime.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1044.pdf`
