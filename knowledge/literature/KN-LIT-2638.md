---
id: KN-LIT-2638
type: literature
title: "Automated Design of Cryptographic Devices Resistant to Multiple Side-Channel Attacks"
authors:
  - "Konrad Kulikowski"
  - "Alexander Smirnov"
  - "Alexander Taubin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, mov-fr, provable-security, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Balanced dynamic dual-rail gates and asynchronous circuits have been shown, if implemented correctly, to have natural and efficient resistance to side-channel attacks. Despite their benefits for security applications they have not been adapted to current mainstream designs due to the lack of electronic design automation support and their nonstandard or proprietary design methodologies.

## Key claims (as reported)
- We present a novel asynchronous fine-grain pipeline synthesis methodology that addresses these limitations.
- It allows synthesis of asynchronous quasi delay insensitive circuits from standard high-level hardware description language (HDL) specifications.
- We briefly present a proof of concept differential dynamic power balanced micropipeline library cells that are approximately 6 times more balanced than the best (differential dynamic) cells designed using previous balancing methods.
- An implementation of the Advanced Encryption Standard based on these balanced cells and synthesized using our tool flow shows a 6.6 times throughput improvement over the synchronous automatically pipelined implementation using the same TSMC 0.18μm technology synthesized from the same HDL specification.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31 (1).pdf`
- `downloads/31 (2).pdf`
- `downloads/31 (3).pdf`
- `downloads/31.pdf`
