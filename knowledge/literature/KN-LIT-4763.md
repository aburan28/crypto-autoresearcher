---
id: KN-LIT-4763
type: literature
title: "Linicrypt: A Model for Practical Cryptography?"
authors:
  - "Brent Carmer"
  - "Mike Rosulek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, provable-security, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A wide variety of objectively practical cryptographic schemes can be constructed using only symmetric-key operations and linear operations. To formally study this restricted class of cryptographic algorithms, we present a new model called Linicrypt.

## Key claims (as reported)
- A Linicrypt program has access to a random oracle whose inputs and outputs are field elements, and otherwise manipulates data only via fixed linear combinations.
- Our main technical result is that it is possible to decide in polynomial time whether two given Linicrypt programs induce computationally indistinguishable distributions (against arbitrary PPT adversaries, in the random oracle model).
- We show also that indistinguishability of Linicrypt programs can be expressed as an existential formula, making the model amenable to automated program synthesis.
- In other words, it is possible to use a SAT/SMT solver to automatically generate Linicrypt programs satisfying a given security constraint.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160404 (1).pdf`
- `downloads/98160404.pdf`
