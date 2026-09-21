---
id: KN-LIT-2204
type: literature
title: "A Provable-Security Treatment of the Key-Wrap Problem"
authors:
  - "Phillip Rogaway"
  - "Thomas Shrimpton"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a provable-security treatment for the key-wrap problem, providing definitions, constructions, and proofs. We suggest that key-wrap’s goal is security in the sense of deterministic authenticated-encryption (DAE), a notion that we put forward.

## Key claims (as reported)
- We also provide an alternative notion, a pseudorandom injection (PRI), which we prove to be equivalent.
- We provide a DAE construction, SIV, analyze its concrete security, develop a blockcipher-based instantiation of it, and suggest that the method makes a desirable alternative to the schemes of the X9.102 draft standard.
- The construction incorporates a method to turn a PRF that operates on a string into an equally efficient PRF that operates on a vector of strings, a problem of independent interest.
- Finally, we consider IVbased authenticated-encryption (AE) schemes that are maximally forgiving of repeated IVs, a goal we formalize as misuse-resistant AE.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040377 (1).pdf`
- `downloads/40040377 (2).pdf`
- `downloads/40040377 (3).pdf`
- `downloads/40040377.pdf`
