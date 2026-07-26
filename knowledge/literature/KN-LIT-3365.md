---
id: KN-LIT-3365
type: literature
title: "Decentralizing Inner-Product Functional Encryption"
authors:
  - "Michel Abdalla"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multi-client functional encryption (MCFE) is a more flexible variant of functional encryption whose functional decryption involves multiple ciphertexts from different parties. Each party holds a different secret key and can independently and adaptively be corrupted by the adversary.

## Key claims (as reported)
- We present two compilers for MCFE schemes for the innerproduct functionality, both of which support encryption labels.
- Our first compiler transforms any scheme with a special key-derivation property into a decentralized scheme, as defined by Chotard et al.
- (ASIACRYPT 2018), thus allowing for a simple distributed way of generating functional decryption keys without a trusted party.
- Our second compiler allows to lift an unnatural restriction present in existing (decentralized) MCFE schemes, which requires the adversary to ask for a ciphertext from each party.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420242 (1).pdf`
- `downloads/114420242.pdf`
