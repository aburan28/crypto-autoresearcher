---
id: KN-LIT-4743
type: literature
title: "Limits on the Power of Zero-Knowledge Proofs in Cryptographic Constructions"
authors:
  - "Zvika Brakerski"
  - "Jonathan Katz"
  - "Gil Segev"
  - "Arkady Yerukhimovich"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
For over 20 years, black-box impossibility results have been used to argue the infeasibility of constructing certain cryptographic primitives (e.g., key agreement) from others (e.g., one-way functions). A widely recognized limitation of such impossibility results, however, is that they say nothing about the usefulness of (known) nonblack-box techniques.

## Key claims (as reported)
- This is unsatisfying, as we would at least like to rule out constructions using the set of techniques we have at our disposal.
- With this motivation in mind, we suggest a new framework for blackbox constructions that encompasses constructions with a nonblack-box flavor: specifically, those that rely on zero-knowledge proofs relative to some oracle.
- We show that our framework is powerful enough to capture the Naor-Yung/Sahai paradigm for building a (shielding) CCA-secure public-key encryption scheme from a CPA-secure one, something ruled out by prior black-box separation results.
- On the other hand, we show that several black-box impossibility results still hold even in a setting that allows for zero-knowledge proofs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65970555 (1).pdf`
- `downloads/65970555 (2).pdf`
- `downloads/65970555 (3).pdf`
- `downloads/65970555.pdf`
