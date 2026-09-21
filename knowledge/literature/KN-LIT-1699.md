---
id: KN-LIT-1699
type: literature
title: "Is PSI Really Faster Than PSU? Achieving Efficient PSU with Invertible Bloom Filters"
authors:
  - "Lucas Piske"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/376"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/376"
tags: [mpc, pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Private Set Union (PSU) enables two parties to compute the union of their private sets without revealing anything beyond the union itself. Existing PSU protocols remain much slower than private set intersection (PSI), often by a factor of around 30×.

## Key claims (as reported)
- In this work, we present the first PSU protocol based on Invertible Bloom Lookup Tables (IBLTs), introducing a fundamentally new framework that departs from traditional, inefficient approaches.
- Our protocol exploits structural invariants between each party’s IBLTs and their union to compute the union efficiently without explicitly constructing a combined IBLT.
- Central to our approach is the notion of union peelability, which allows union elements to be recovered directly from the original IBLTs.
- We securely implement this functionality using only Oblivious Transfer (OT) and Oblivious Pseudorandom Function (OPRF) for equality checks, ensuring no information beyond the union is leaked.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-376.pdf`
