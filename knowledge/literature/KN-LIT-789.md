---
id: KN-LIT-789
type: literature
title: "New Representations of the AES Key Schedule"
authors:
  - "Gaëtan Leurent"
  - "Clara Pernot"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/1253"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/1253"
tags: [cryptanalysis, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present a new representation of the AES key schedule, with some implications to the security of AES-based schemes. In particular, we show that the AES-128 key schedule can be split into four independent parallel computations operating on 32-bit chunks, up to linear transformation.

## Key claims (as reported)
- Surprisingly, this property has not been described in the literature after more than 20 years of analysis of AES.
- We show two consequences of our new representation, improving previous cryptanalysis results of AES-based schemes.
- First, we observe that iterating an odd number of key schedule rounds results in a permutation with short cycles.
- This explains an observation of Khairallah on mixFeed, a second-round candidate in the NIST lightweight competition.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960202 (1).pdf`
- `downloads/126960202.pdf`
- `downloads/2020-1253.pdf`
