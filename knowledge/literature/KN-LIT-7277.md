---
id: KN-LIT-7277
type: literature
title: "Tweakable Block Ciphers Secure Beyond the Birthday Bound in the Ideal Cipher Model"
authors:
  - "ByeongHak Lee"
  - "Jooyoung Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a new construction of tweakable block ciphers from standard block ciphers. Our construction, dubbed XHX2, is the cascade of two independent XHX block ciphers, so it makes two calls to the underlying block cipher using tweak-dependent keys.

## Key claims (as reported)
- We prove the security of XHX2 up to min{22(n+m)/3 , 2n+m/2 } queries (ignoring logarithmic factors) in the ideal cipher model, when the block cipher operates on nbit blocks using m-bit keys.
- The XHX2 tweakable block cipher is the first construction that achieves beyond-birthday-bound security with respect to the input size of the underlying block cipher in the ideal cipher model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272117 (1).pdf`
- `downloads/11272117.pdf`
