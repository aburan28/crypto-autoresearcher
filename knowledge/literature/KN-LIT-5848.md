---
id: KN-LIT-5848
type: literature
title: "Practical Large-scale Distributed Key Generation"
authors:
  - "John Canny"
  - "Stephen Sorkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Generating a distributed key, where a constant fraction of the players can reconstruct the key, is an essential component of many largescale distributed computing tasks such as fully peer-to-peer computation and voting schemes. Previous solutions relied on a dedicated broadcast channel and had at least quadratic cost per player to handle a constant fraction of adversaries, which is not practical for extremely large sets of participants.

## Key claims (as reported)
- We present a new distributed key generation algorithm, sparse matrix DKG, for discrete-log based cryptosystems that requires only polylogarithmic communication and computation per player and no global broadcast.
- This algorithm has nearly the same optimal threshold as previous ones, allowing up to a 12 −  fraction of adversaries, but is probabilistic and has an arbitrarily small failure probability.
- In addition, this algorithm admits a rigorous proof of security.
- We also introduce the notion of matrix evaluated DKG, which encompasses both the new sparse matrix algorithm and the familiar polynomial based ones.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/paper (1).pdf`
- `downloads/paper (5).pdf`
- `downloads/paper (7).pdf`
