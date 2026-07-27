---
id: KN-LIT-4467
type: literature
title: "Incremental Multiset Hash Functions and Their Application to Memory Integrity Checking Dwaine Clarke? , Srinivas Devadas, Marten van Dijk??"
authors:
  - "Blaise Gassend"
  - "G. Edward Suh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, finite-field, hash, lattice, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new cryptographic tool: multiset hash functions. Unlike standard hash functions which take strings as input, multiset hash functions operate on multisets (or sets).

## Key claims (as reported)
- They map multisets of arbitrary finite size to strings (hashes) of fixed length.
- They are incremental in that, when new members are added to the multiset, the hash can be updated in time proportional to the change.
- The functions may be multiset-collision resistant in that it is difficult to find two multisets which produce the same hash, or just set-collision resistant in that it is difficult to find a set and a multiset which produce the same hash.
- We demonstrate how set-collision resistant multiset hash functions make an existing offline memory integrity checker secure against active adversaries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/paper (4).pdf`
- `downloads/paper (6).pdf`
- `downloads/paper.pdf`
