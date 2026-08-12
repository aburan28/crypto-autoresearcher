---
id: KN-LIT-6817
type: literature
title: "Strengthening Digital Signatures via Randomized Hashing"
authors:
  - "Shai Halevi∗"
  - "Hugo Krawczyk∗∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose randomized hashing as a mode of operation for cryptographic hash functions intended for use with standard digital signatures and without necessitating of any changes in the internals of the underlying hash function (e.g., the SHA family) or in the signature algorithms (e.g., RSA or DSA). The goal is to free practical digital signature schemes from their current reliance on strong collision resistance by basing the security of these schemes on significantly weaker properties of the underlying hash function, thus providing a safety net in case the (current or future) hash functions in use turn out to be less resilient to collision search than initially thought.

## Key claims (as reported)
- We design a specific mode of operation that takes into account engineering considerations (such as simplicity, efficiency and compatibility with existing implementations) as well as analytical soundness.
- Specifically, the scheme consists of a regular use of the hash function with randomization applied only to the message before it is input to the hash function.
- We formally show the sufficiency of weaker than collision-resistance assumptions for proving the security of the scheme.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/41170039 (1).pdf`
- `downloads/41170039 (2).pdf`
- `downloads/41170039 (3).pdf`
- `downloads/41170039.pdf`
