---
id: KN-LIT-3951
type: literature
title: "Friet: an Authenticated Encryption Scheme with Built-in Fault Detection"
authors:
  - "Thierry Simon"
  - "Lejla Batina"
  - "Joan Daemen"
  - "Vincent Grosso"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work we present a duplex-based authenticated encryption scheme Friet based on a new permutation called Friet-P. We designed Friet-P with a novel approach for cryptographic permutations and block ciphers that takes fault-attack resistance into account and that we introduce in this paper.

## Key claims (as reported)
- In this method, we build a permutation fC to be embedded in a larger one, f .
- First, we define f as a sequence of steps that all abide a chosen error-correcting code C, i.e., that map C-codewords to C-codewords.
- Then, we embed fC in f by first encoding its input to an element of C, applying f and then decoding back from C.
- This last step detects a fault when the output of f is not in C.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105367 (1).pdf`
- `downloads/12105367.pdf`
