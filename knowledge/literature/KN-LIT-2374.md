---
id: KN-LIT-2374
type: literature
title: "Aggregate and Verifiably Encrypted Signatures from Bilinear Maps"
authors:
  - "Dan Boneh"
  - "Craig Gentry"
  - "Ben Lynn"
  - "Hovav Shacham"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An aggregate signature scheme is a digital signature that supports aggregation: Given n signatures on n distinct messages from n distinct users, it is possible to aggregate all these signatures into a single short signature. This single signature (and the n original messages) will convince the verifier that the n users did indeed sign the n original messages (i.e., user i signed message Mi for i = 1, . . . , n).

## Key claims (as reported)
- In this paper we introduce the concept of an aggregate signature, present security models for such signatures, and give several applications for aggregate signatures.
- We construct an efficient aggregate signature from a recent short signature scheme based on bilinear maps due to Boneh, Lynn, and Shacham.
- Aggregate signatures are useful for reducing the size of certificate chains (by aggregating all signatures in the chain) and for reducing message size in secure routing protocols such as SBGP.
- We also show that aggregate signatures give rise to verifiably encrypted signatures.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560416 (1).pdf`
- `downloads/26560416 (2).pdf`
- `downloads/26560416.pdf`
