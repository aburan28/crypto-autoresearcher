---
id: KN-LIT-4033
type: literature
title: "Functional Encryption: Definitions and Challenges"
authors:
  - "Dan Boneh"
  - "Amit Sahai"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate the formal study of functional encryption by giving precise definitions of the concept and its security. Roughly speaking, functional encryption supports restricted secret keys that enable a key holder to learn a specific function of encrypted data, but learn nothing else about the data.

## Key claims (as reported)
- For example, given an encrypted program the secret key may enable the key holder to learn the output of the program on a specific input without learning anything else about the program.
- We show that defining security for functional encryption is non-trivial.
- First, we show that a natural game-based definition is inadequate for some functionalities.
- We then present a natural simulation-based definition and show that it (provably) cannot be satisfied in the standard model, but can be satisfied in the random oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65970250 (1).pdf`
- `downloads/65970250 (2).pdf`
- `downloads/65970250 (3).pdf`
- `downloads/65970250.pdf`
