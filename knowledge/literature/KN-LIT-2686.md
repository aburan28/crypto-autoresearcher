---
id: KN-LIT-2686
type: literature
title: "Between a Rock and a Hard Place: Interpolating"
authors:
  - "Between MPC"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a computationally secure MPC protocol for threshold adversaries which is parametrized by a value L. When L = 2 we obtain a classical form of MPC protocol in which interaction is required for multiplications, as L increases interaction is reduced, in that one requires interaction only after computing a higher degree function.

## Key claims (as reported)
- When L approaches infinity one obtains the FHE based protocol of Gentry, which requires no interaction.
- Thus one can trade communication for computation in a simple way.
- Our protocol is based on an interactive protocol for “bootstrapping” a somewhat homomorphic encryption (SHE) scheme.
- The key contribution is that our presented protocol is highly communication efficient enabling us to obtain reduced communication when compared to traditional MPC protocols for relatively small values of L.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/82700222 (1).pdf`
- `downloads/82700222 (2).pdf`
- `downloads/82700222 (3).pdf`
- `downloads/82700222.pdf`
