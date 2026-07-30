---
id: KN-LIT-6916
type: literature
title: "Symmetrically and Asymmetrically Hard Cryptography"
authors:
  - "Alex Biryukov"
  - "Léo Perrin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The main efficiency metrics for a cryptographic primitive are its speed, its code size and its memory complexity. For a variety of reasons, many algorithms have been proposed that, instead of optimizing, try to increase one of these hardness forms.

## Key claims (as reported)
- We present for the first time a unified framework for describing the hardness of a primitive along any of these three axes: code-hardness, timehardness and memory-hardness.
- This unified view allows us to present modular block cipher and sponge constructions which can have any of the three forms of hardness and can be used to build any higher level symmetric primitive: hash function, PRNG, etc.
- We also formalize a new concept: asymmetric hardness.
- It creates two classes of users: common users have to compute a function with a certain hardness while users knowing a secret can compute the same function in a far cheaper way.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240122 (1).pdf`
- `downloads/106240122.pdf`
