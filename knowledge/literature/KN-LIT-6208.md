---
id: KN-LIT-6208
type: literature
title: "Relational Hash: Probabilistic Hash for Verifying Relations, Secure against Forgery and More"
authors:
  - "Avradip Mandal"
  - "Arnab Roy"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Traditional cryptographic hash functions allow one to easily check whether the original plaintexts are equal or not, given a pair of hash values. Probabilistic hash functions extend this concept where given a probabilistic hash of a value and the value itself, one can efficiently check whether the hash corresponds to the given value.

## Key claims (as reported)
- However, given distinct probabilistic hashes of the same value it is not possible to check whether they correspond to the same value.
- In this work we introduce a new cryptographic primitive called Relational Hash using which, given a pair of (relational) hash values, one can determine whether the original plaintexts were related or not.
- We formalize various natural security notions for the Relational Hash primitive - one-wayness, twin one-wayness, unforgeability and oracle simulatibility.
- We develop a Relational Hash scheme for discovering linear relations among bit-vectors (elements of Fn 2 ) and Fp -vectors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160179 (1).pdf`
- `downloads/92160179 (2).pdf`
- `downloads/92160179.pdf`
