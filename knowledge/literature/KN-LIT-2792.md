---
id: KN-LIT-2792
type: literature
title: "Breaking Grain-128 with Dynamic Cube Attacks"
authors:
  - "Itai Dinur"
  - "Adi Shamir"
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
We present a new variant of cube attacks called a dynamic cube attack. Whereas standard cube attacks [4] find the key by solving a system of linear equations in the key bits, the new attack recovers the secret key by exploiting distinguishers obtained from cube testers.

## Key claims (as reported)
- Dynamic cube attacks can create lower degree representations of the given cipher, which makes it possible to attack schemes that resist all previously known attacks.
- In this paper we concentrate on the well-known stream cipher Grain-128 [6], on which the best known key recovery attack [15] can recover only 2 key bits when the number of initialization rounds is decreased from 256 to 213.
- Our first attack runs in practical time complexity and recovers the full 128-bit key when the number of initialization rounds in Grain-128 is reduced to 207.
- Our second attack breaks a Grain-128 variant with 250 initialization rounds and is faster than exhaustive search by a factor of about 228 .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/67330172 (1).pdf`
- `downloads/67330172 (2).pdf`
- `downloads/67330172 (3).pdf`
- `downloads/67330172.pdf`
