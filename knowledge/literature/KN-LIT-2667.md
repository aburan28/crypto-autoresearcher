---
id: KN-LIT-2667
type: literature
title: "Batch-OT with Optimal Rate"
authors:
  - "Zvika Brakerski"
  - "Pedro Branco Nico Döttling"
  - "Sihang Pu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that it is possible to perform n independent copies of 1-out-of-2 oblivious transfer in two messages, where the communication complexity of the receiver and sender (each) is n(1 + o(1)) for sufficiently large n. Note that this matches the information-theoretic lower bound.

## Key claims (as reported)
- Prior to this work, this was only achievable by using the heavy machinery of rate-1 fully homomorphic encryption (Rate-1 FHE, Brakerski et al., TCC 2019).
- To achieve rate-1 both on the receiver’s and sender’s end, we use the LPN assumption, with slightly sub-constant noise rate 1/m for any  > 0 together with either the DDH, QR or LWE assumptions.
- In terms of efficiency, our protocols only rely on linear homomorphism, as opposed to the FHE-based solution which inherently requires an expensive “bootstrapping” operation.
- We believe that in terms of efficiency we compare favorably to existing batch-OT protocols, while achieving superior communication complexity.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760280 (1).pdf`
- `downloads/132760280.pdf`
