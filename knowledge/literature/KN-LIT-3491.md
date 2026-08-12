---
id: KN-LIT-3491
type: literature
title: "Dynamic Accumulators and Application to Efficient Revocation of Anonymous Credentials"
authors:
  - "Jan Camenisch"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, quantum, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the notion of a dynamic accumulator. An accumulator scheme allows one to hash a large set of inputs into one short value, such that there is a short proof that a given input was incorporated into this value.

## Key claims (as reported)
- A dynamic accumulator allows one to dynamically add and delete a value, such that the cost of an add or delete is independent of the number of accumulated values.
- We provide a construction of a dynamic accumulator and an efficient zero-knowledge proof of knowledge of an accumulated value.
- We prove their security under the strong RSA assumption.
- We then show that our construction of dynamic accumulators enables efficient revocation of anonymous credentials, and membership revocation for recent group signature and identity escrow schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420061 (1).pdf`
- `downloads/24420061 (2).pdf`
- `downloads/24420061.pdf`
