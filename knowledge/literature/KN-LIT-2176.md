---
id: KN-LIT-2176
type: literature
title: "A Parallel Repetition Theorem for Leakage Resilience"
authors:
  - "Zvika Brakerski"
  - "Yael Tauman Kalai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A leakage resilient encryption scheme is one which stays secure even against an attacker that obtains a bounded amount of side information on the secret key (say λ bits of “leakage”). A fundamental question is whether parallel repetition amplifies leakage resilience.

## Key claims (as reported)
- Namely, if we secret share our message, and encrypt the shares under two independent keys, will the resulting scheme be resilient to 2λ bits of leakage?
- Surprisingly, Lewko and Waters (FOCS 2010) showed that this is false.
- They gave an example of a public-key encryption scheme that is (CPA) resilient to λ bits of leakage, and yet its 2-repetition is not resilient to even (1 + )λ bits of leakage.
- In their counter-example, the repeated schemes share secretly generated public parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/71940141 (1).pdf`
- `downloads/71940141 (2).pdf`
- `downloads/71940141 (3).pdf`
- `downloads/71940141.pdf`
