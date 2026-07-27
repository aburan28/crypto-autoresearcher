---
id: KN-LIT-947
type: literature
title: "A Note on Reimplementing the Castryck-Decru Attack and Lessons Learned for SageMath"
authors:
  - "Rémy Oudompheng"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1283"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1283"
tags: [cryptanalysis, elliptic-curve, hash, isogeny, jacobian, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This note describes the implementation of the Castryck-Decru key recovery attack on SIDH using the computer algebra system, SageMath. We describe in detail alternate computation methods for the isogeny steps of the original attack ((2, 2)isogenies from a product of elliptic curves and from a Jacobian), using explicit formulas to compute values of these isogenies at given points, motivated by both performance considerations and working around SageMath limitations.

## Key claims (as reported)
- A performance analysis is provided, with focus given to the various algorithmic and SageMath specific improvements made during development, which in total accumulated in approximately an eight-fold performance improvement compared with a naïve reimplementation of the proof of concept.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-1283.pdf`
