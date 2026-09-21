---
id: KN-LIT-6936
type: literature
title: "TEC-Tree: A Low-Cost, Parallelizable Tree for"
authors:
  - "Gilles Sassatelli"
  - "Pierre Guillemin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Replay attacks are often the most costly attacks to thwart when dealing with off-chip memory integrity. With a trusted System-on-Chip, the existing countermeasures against replay require a large amount of on-chip memory to provide tamper-proof storage for metadata such as hash values or nonces.

## Key claims (as reported)
- Tree-based strategies can be deployed to reduce this unacceptable overhead; for example, the well-known Merkle tree technique decreases this overhead to a single hash value.
- However, it comes at the cost of performancekilling characteristics for embedded systems – e.g. non-parallelizable hash computations on tree updates.
- In this paper, we propose an alternative solution: the Tamper-Evident Counter Tree (TEC-Tree).
- It allows for tamper-evident offchip storage of the nonces involved in a replay countermeasure; TEC-Tree parallelizes the computations involved in both the authentication and tree update processes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270289 (1).pdf`
- `downloads/47270289 (2).pdf`
- `downloads/47270289 (3).pdf`
- `downloads/47270289.pdf`
