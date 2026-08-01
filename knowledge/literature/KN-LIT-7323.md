---
id: KN-LIT-7323
type: literature
title: "Two-server Distributed ORAM with Sublinear"
authors:
  - "Constant Rounds"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Distributed ORAM (DORAM) is a multi-server variant of Oblivious RAM. Originally proposed to lower bandwidth, DORAM has recently been of great interest due to its applicability to secure computation in the RAM model, where circuit complexity and rounds of communication are equally important metrics of efficiency.

## Key claims (as reported)
- All prior DORAM constructions either involve linear work per server (e.g., Floram) or logarithmic rounds of communication between servers (e.g., square root ORAM).
- In this work, we construct the first DORAM schemes in the 2server, semi-honest setting that simultaneously achieve sublinear server computation and constant rounds of communication.
- We provide two constant-round constructions, one based on square root ORAM that has √ O( N log N ) local computation and another based on secure computation of a doubly efficient PIR that achieves local computation of O(N  ) for any  > 0 but that allows the servers to distinguish between reads and writes.
- As a building block in the latter construction, we provide secure computation protocols for evaluation and interpolation of multivariate polynomials based on the Fast Fourier Transform, which may be of independent interest.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110200 (1).pdf`
- `downloads/127110200.pdf`
