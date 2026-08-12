---
id: KN-LIT-3890
type: literature
title: "Finding Second Preimages of Short Messages for Hamsi-256"
authors:
  - "Thomas Fuhr"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we study the second preimage resistance of Hamsi-256, a second round SHA-3 candidate. We show that it is possible to find affine equations between some input bits and some output bits on the 3-round compression function.

## Key claims (as reported)
- This property enables an attacker to find pseudo preimages for the Hamsi-256 compression function.
- The pseudo preimage algorithm can be used to find second preimages of the digests of messages M with complexity 2251.3 , which is lower than the best generic attacks when M is short.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477020 (1).pdf`
- `downloads/6477020 (2).pdf`
- `downloads/6477020 (3).pdf`
- `downloads/6477020.pdf`
