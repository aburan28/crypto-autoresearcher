---
id: KN-LIT-6547
type: literature
title: 'Semantically Secure Order-Revealing Encryption: Multi-Input'
authors:
- Amit Sahai
- Mark Zhandry
- Joe Zimmerman
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags:
- order-revealing-encryption
- multilinear-maps
- provable-security
confidence: reported
citation_verified: read
added: '2026-07-24'
superseded_by: null
---

## Contribution
Deciding “greater-than” relations among data items just given their encryptions is at the heart of search algorithms on encrypted data, most notably, non-interactive binary search on encrypted data. Orderpreserving encryption provides one solution, but provably provides only limited security guarantees.

## Key claims (as reported)
- Two-input functional encryption is another approach, but requires the full power of obfuscation machinery and is currently not implementable.
- We construct the first implementable encryption system supporting greaterthan comparisons on encrypted data that provides the “best-possible” semantic security.
- In our scheme there is a public algorithm that given two ciphertexts as input, reveals the order of the corresponding plaintexts and nothing else.
- Our constructions are inspired by obfuscation techniques, but do not use obfuscation.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560194 (1).pdf`
- `downloads/90560194.pdf`
