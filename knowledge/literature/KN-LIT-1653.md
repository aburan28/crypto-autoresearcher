---
id: KN-LIT-1653
type: literature
title: "Fault Injection Attacks Against zkSTARKs"
authors:
  - "Alexander Dalton"
  - "Daniel Page"
  - "Markus Schofnegger"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/835"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/835"
tags: [cryptanalysis, pairing, pqc, quantum, side-channel, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fault injection attacks targeting schemes with zero-knowledge (ZK) properties are relatively absent in the wider literature. One of the few examples has recently shown a ZK signature scheme to be vulnerable to fault injection attacks.

## Key claims (as reported)
- In this paper, we detail candidate fault injection attacks against zero-knowledge scalable transparent argument of knowledge (zkSTARK) provers, designed to violate zero knowledge capabilities. zkSTARK proving systems are complex, with a huge amount of diversity in implementation specifics.
- We match the variety within the STARK implementation ecosystem, proposing a variety of fault injection attacks against different popular algorithmic primitives.
- To the best of our knowledge, this marks the first exploration of the fault injection surface of zkSTARKs, and of the wider class of general-purpose ZK proving systems.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-835.pdf`
