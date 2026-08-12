---
id: KN-LIT-7389
type: literature
title: "Universal Proxy Re-Encryption"
authors:
  - "Nico Döttling"
  - "Ryo Nishimaki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We put forward the notion of universal proxy re-encryption (UPRE). A UPRE scheme enables a proxy to convert a ciphertext under a (delegator) public key of any existing public-key encryption (PKE) scheme into another ciphertext under a (delegatee) public key of any existing PKE scheme (possibly different from the delegator one).

## Key claims (as reported)
- The proxy has a re-encryption key generated from the delegator’s secret key and the delegatee public key.
- Thus UPRE generalizes proxy re-encryption by supporting arbitrary PKE schemes and allowing to convert ciphertexts into ones of possibly different PKE schemes.
- In this work, we – provide syntax and definitions for both UPRE and a variant we call relaxed UPRE.
- The relaxed variant means that decryption algorithms for re-encrypted ciphertexts are slightly modified but still only use the original delegatee secret keys for decryption. – construct a UPRE based on probabilistic indistinguishability obfuscation (PIO).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110171 (1).pdf`
- `downloads/127110171.pdf`
