---
id: KN-LIT-2137
type: literature
title: "A New Class of Collision Attacks and its Application to DES"
authors:
  - "Kai Schramm"
  - "Thomas Wollinger"
  - "Christof Paar"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Until now in cryptography the term collision was mainly associated with the surjective mapping of different inputs to an equal output of a hash function. Previous collision attacks were only able to detect collisions at the output of a particular function.

## Key claims (as reported)
- In this publication we introduce a new class of attacks which originates from Hans Dobbertin and is based on the fact that side channel analysis can be used to detect internal collisions.
- We applied our attack against the widely used Data Encryption Standard (DES).
- We exploit the fact that internal collisions can be caused in three adjacent S-Boxes of DES [DDQ84] in order to gain information about the secret key-bits.
- As result, we were able to exploit an internal collision with a minimum of 140 encryptions1 yielding 10.2 key-bits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/28870216 (1).pdf`
- `downloads/28870216 (2).pdf`
- `downloads/28870216.pdf`
