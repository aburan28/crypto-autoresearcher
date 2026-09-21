---
id: KN-LIT-7436
type: literature
title: "Using Bleichenbacher’s Solution to the Hidden"
authors:
  - "Number Problem to Attack Nonce Leaks in"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, hash, lattice, protocol, provable-security, quantum, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we describe an attack against nonce leaks in 384-bit ECDSA using an FFT-based attack due to Bleichenbacher. The signatures were computed by a modern smart card.

## Key claims (as reported)
- We extracted the low-order bits of each nonce using a template-based power analysis attack against the modular inversion of the nonce.
- We also developed a BKZ-based method for the range reduction phase of the attack, as it was impractical to collect enough signatures for the collision searches originally used by Bleichenbacher.
- We confirmed our attack by extracting the entire signing key using a 5-bit nonce leak from 4 000 signatures.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860105 (1).pdf`
- `downloads/80860105 (2).pdf`
- `downloads/80860105 (3).pdf`
- `downloads/80860105.pdf`
