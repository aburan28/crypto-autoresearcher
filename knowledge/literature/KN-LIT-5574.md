---
id: KN-LIT-5574
type: literature
title: "On the Security of Keyed Hashing Based on Public Permutations"
authors:
  - "Jonathan Fuchs("
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Doubly-extendable cryptographic keyed functions (deck) generalize the concept of message authentication codes (MAC) and stream ciphers in that they support variable-length strings as input and return variable-length strings as output. A prominent example of building deck functions is Farfalle, which consists of a set of public permutations and rolling functions that are used in its compression and expansion layers.

## Key claims (as reported)
- By generalizing the compression layer of Farfalle, we prove its universality in terms of the probability of differentials over the public permutation used in it.
- As the compression layer of Farfalle is inherently parallel, we compare it to a generalization of a serial compression function inspired by Pelican-MAC.
- The same public permutation may result in different universalities depending on whether the compression is done in parallel or serial.
- The parallel construction consistently performs better than the serial one, sometimes by a big factor.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850098 (1).pdf`
- `downloads/140850098.pdf`
