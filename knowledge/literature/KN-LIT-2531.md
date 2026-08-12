---
id: KN-LIT-2531
type: literature
title: "Analysis of the security of the PSSI problem and cryptanalysis of the Durandal signature scheme"
authors:
  - "Nicolas Aragon"
  - "Victor Dyseryn"
  - "Philippe Gaborit"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pqc, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new attack against the PSSI problem, one of the three problems at the root of security of Durandal, an efficient rank metric code-based signature scheme with a public key size of 15 kB and a signature size of 4 kB, presented at EUROCRYPT’19. Our attack recovers the private key using a leakage of information coming from several signatures produced with the same key.

## Key claims (as reported)
- Our approach is to combine pairs of signatures and perform Cramer-like formulas in order to build subspaces containing a secret element.
- We break all existing parameters of Durandal: the two published sets of parameters claiming a security of 128 bits are broken in respectively 266 and 273 elementary bit operations, and the number of signatures required to finalize the attack is 1,792 and 4,096 respectively.
- We implemented our attack and ran experiments that demonstrated its success with smaller parameters.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850073 (1).pdf`
- `downloads/140850073.pdf`
