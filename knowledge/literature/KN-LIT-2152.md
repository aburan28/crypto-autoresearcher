---
id: KN-LIT-2152
type: literature
title: "A New Mode of Operation for"
authors:
  - "Block Ciphers"
  - "Length-Preserving MACs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new mode of operation, enciphered CBC, for domain extension of length-preserving functions (like block ciphers), which is a variation on the popular CBC mode of operation. Our new mode is twice slower than CBC, but has many (property-preserving) properties not enjoyed by CBC and other known modes.

## Key claims (as reported)
- Most notably, it yields the first constant-rate Variable Input Length (VIL) MAC from any length preserving Fixed Input Length (FIL) MAC.
- This answers the question of Dodis and Puniya from Eurocrypt 2007.
- Further, our mode is a secure domain extender for PRFs (with basically the same security as encrypted CBC).
- This provides a hedge against the security of the block cipher: if the block cipher is pseudorandom, one gets a VIL-PRF, while if it is “only” unpredictable, one “at least” gets a VIL-MAC.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/49650197 (1).pdf`
- `downloads/49650197 (2).pdf`
- `downloads/49650197 (3).pdf`
- `downloads/49650197.pdf`
