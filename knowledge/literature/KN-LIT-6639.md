---
id: KN-LIT-6639
type: literature
title: "Signing a Linear Subspace: Signature Schemes for Network Coding"
authors:
  - "Dan Boneh"
  - "David Freeman"
  - "Jonathan Katz"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, provable-security, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Network coding offers increased throughput and improved robustness to random faults in completely decentralized networks. In contrast to traditional routing schemes, however, network coding requires intermediate nodes to modify data packets en route; for this reason, standard signature schemes are inapplicable and it is a challenge to provide resilience to tampering by malicious nodes.

## Key claims (as reported)
- We propose two signature schemes that can be used in conjunction with network coding to prevent malicious modification of data.
- Our schemes can be viewed as signing linear subspaces in the sense that a signature σ on a subspace V authenticates exactly those vectors in V .
- Our first scheme is (suitably) homomorphic and has constant public-key size and per-packet overhead.
- Our second scheme does not rely on random oracles and is based on weaker assumptions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54430070 (1).pdf`
- `downloads/54430070 (2).pdf`
- `downloads/54430070 (3).pdf`
- `downloads/54430070.pdf`
