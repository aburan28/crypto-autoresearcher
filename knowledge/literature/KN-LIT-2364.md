---
id: KN-LIT-2364
type: literature
title: "Additively Homomorphic IBE from Higher Residuosity"
authors:
  - "Michael Clear"
  - "Ciaran McGoldrick∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, fhe, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an identity-Based encryption (IBE) scheme that is group homomorphic for addition modulo a “large” (i.e. superpolynomial) integer, the first such group homomorphic IBE. Our first result is the construction of an IBE scheme supporting homomorphic addition modulo a poly-sized prime e.

## Key claims (as reported)
- Our construction builds upon the IBE scheme of Boneh, LaVigne and Sabin (BLS).
- BLS relies on a hash function that maps identities to eth residues.
- However there is no known way to securely instantiate such a function.
- Our construction extends BLS so that it can use a hash function that can be securely instantiated.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420239 (1).pdf`
- `downloads/114420239.pdf`
