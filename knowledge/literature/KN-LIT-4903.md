---
id: KN-LIT-4903
type: literature
title: "Merkle-Damgård Revisited : how to Construct a Hash Function"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The most common way of constructing a hash function (e.g., SHA-1) is to iterate a compression function on the input message. The compression function is usually designed from scratch or made out of a block-cipher.

## Key claims (as reported)
- In this paper, we introduce a new security notion for hash-functions, stronger than collision-resistance.
- Under this notion, the arbitrary length hash function H must behave as a random oracle when the fixed-length building block is viewed as a random oracle or an ideal block-cipher.
- The key property is that if a particular construction meets this definition, then any cryptosystem proven secure assuming H is a random oracle remains secure if one plugs in this construction (still assuming that the underlying fixed-length primitive is ideal).
- In this paper, we show that the current design principle behind hash functions such as SHA-1 and MD5 — the (strengthened) Merkle-Damgård transformation — does not satisfy this security notion.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/36210424 (1).pdf`
- `downloads/36210424 (2).pdf`
- `downloads/36210424 (3).pdf`
- `downloads/36210424.pdf`
