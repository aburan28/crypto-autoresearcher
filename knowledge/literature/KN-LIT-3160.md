---
id: KN-LIT-3160
type: literature
title: "Conversion from Arithmetic to Boolean Masking with Logarithmic Complexity"
authors:
  - "Kumar Vadnala"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, quantum, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A general technique to protect a cryptographic algorithm against side-channel attacks consists in masking all intermediate variables with a random value. For cryptographic algorithms combining Boolean operations with arithmetic operations, one must then perform conversions between Boolean masking and arithmetic masking.

## Key claims (as reported)
- At CHES 2001, Goubin described a very elegant algorithm for converting from Boolean masking to arithmetic masking, with only a constant number of operations.
- Goubin also described an algorithm for converting from arithmetic to Boolean masking, but with O(k) operations where k is the addition bit size.
- In this paper we describe an improved algorithm with time complexity O(log k) only.
- Our new algorithm is based on the Kogge-Stone carry look-ahead adder, which computes the carry signal in O(log k) instead of O(k) for the classical ripple carry adder.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400106 (4).pdf`
- `downloads/85400106 (5).pdf`
