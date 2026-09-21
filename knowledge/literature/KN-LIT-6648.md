---
id: KN-LIT-6648
type: literature
title: "Simple and Efficient Two-Server ORAM"
authors:
  - "S. Dov Gordon"
  - "Jonathan Katz"
  - "Xiao Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show a protocol for two-server oblivious RAM (ORAM) that is simpler and more efficient than the best prior work. Our construction combines any tree-based ORAM with an extension of a twoserver private information retrieval scheme by Boyle et al., and is able to avoid recursion and thus use only one round of interaction.

## Key claims (as reported)
- In addition, our scheme has a very cheap initialization phase, making it well suited for RAM-based secure computation.
- Although our scheme requires the servers to perform a linear scan over the entire data, the cryptographic computation involved consists only of block-cipher evaluations.
- A practical instantiation of our protocol has excellent concrete parameters: for storing an N -element array of arbitrary size data blocks with statistical security parameter λ, the servers each store 4N encrypted blocks, the client stores λ + 2 log N blocks, and the total communication per logical access is roughly 10 log N encrypted blocks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272238 (1).pdf`
- `downloads/11272238.pdf`
