---
id: KN-LIT-7114
type: literature
title: "Threshold Private Set Intersection with Better Communication Complexity"
authors:
  - "Satrajit Ghosh"
  - "Mark Simkin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given l parties with sets X1 , . . . , Xl of size n, we would like to securely compute the intersection ∩li=1 Xi , if it is larger than n − t for some threshold t, without revealing any other additional information. It has previously been shown (Ghosh and Simkin, Crypto 2019) that this function can be securely computed with a communication complexity that only depends on t and in particular does not depend on n.

## Key claims (as reported)
- For small values of t, this results in protocols that have a communication complexity that is sublinear in the size of the inputs.
- Current protocols either rely on fully homomorphic encryption or have an at least quadratic dependency on the parameter t.
- In this work, we construct protocols with a quasilinear dependency on t from simple assumptions like additively homomorphic encryption and oblivious transfer.
- All existing approaches, including ours, rely on protocols for computing a single bit, which indicates whether the intersection is larger than n−t without actually computing it.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940135 (1).pdf`
- `downloads/13940135.pdf`
