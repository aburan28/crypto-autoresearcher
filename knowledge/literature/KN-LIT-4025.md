---
id: KN-LIT-4025
type: literature
title: "Functional Encryption for Regular Languages"
authors:
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a functional encryption system that supports functionality for regular languages. In our system a secret key is associated with a Deterministic Finite Automata (DFA) M .

## Key claims (as reported)
- A ciphertext CT encrypts a message m and is associated with an arbitrary length string w.
- A user is able to decrypt the ciphertext CT if and only if the DFA M associated with his private key accepts the string w.
- Compared with other known functional encryption systems, this is the first system where the functionality is capable of recognizing an unbounded language.
- For example, in (Key-Policy) Attribute-Based Encryption (ABE) a private key SK is associated with a single boolean formula φ which operates over a fixed number of boolean variables from the ciphertext.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170217 (1).pdf`
- `downloads/74170217 (2).pdf`
- `downloads/74170217 (3).pdf`
- `downloads/74170217 (4).pdf`
- `downloads/74170217 (5).pdf`
- `downloads/74170217.pdf`
