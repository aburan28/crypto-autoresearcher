---
id: KN-LIT-4839
type: literature
title: "Making Public Key Functional Encryption"
authors:
  - "Function Private"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We put forth a new notion of distributed public key functional encryption. In such a functional encryption scheme, the secret key for a function f will be split into shares skfi .

## Key claims (as reported)
- Given a ciphertext ct that encrypts a message x, a secret key share skfi , one can evaluate and obtain a shared value yi .
- Adding all the shares up can recover the actual value of f (x), while partial shares reveal nothing about the plaintext.
- More importantly, this new model allows us to establish function privacy which was not possible in the setting of regular public key functional encryption.
- We formalize such notion and construct such a scheme from any public key functional encryption scheme together with learning with error assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770218 (1).pdf`
- `downloads/10770218 (2).pdf`
- `downloads/10770218 (3).pdf`
- `downloads/10770218 (4).pdf`
- `downloads/10770218.pdf`
