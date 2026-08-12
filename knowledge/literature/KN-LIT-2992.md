---
id: KN-LIT-2992
type: literature
title: "Compact Multi-Signatures for Smaller Blockchains"
authors:
  - "Dan Boneh"
  - "Manu Drijvers"
  - "Gregory Neven"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct new multi-signature schemes that provide new functionality. Our schemes are designed to reduce the size of the Bitcoin blockchain, but are useful in many other settings where multi-signatures are needed.

## Key claims (as reported)
- All our constructions support both signature compression and public-key aggregation.
- Hence, to verify that a number of parties signed a common message m, the verifier only needs a short multisignature, a short aggregation of their public keys, and the message m.
- We give new constructions that are derived from Schnorr signatures and from BLS signatures.
- Our constructions are in the plain public key model, meaning that users do not need to prove knowledge or possession of their secret key.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272141 (1).pdf`
- `downloads/11272141.pdf`
