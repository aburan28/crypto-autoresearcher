---
id: KN-LIT-1105
type: literature
title: "Exploring Multi-Task Learning in the Context of Masked AES Implementations"
authors:
  - "Thomas Marquet"
  - "Elisabeth Oswald"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/006"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/006"
tags: [mov-fr, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Deep learning is very efficient at breaking masked implementations even when the attacker does not assume knowledge of the masks. However, recent works pointed out a significant challenge: overcoming the initial learning plateau.

## Key claims (as reported)
- This paper discusses the advantages of multi-task learning to break through the initial plateau consistently.
- We investigate different ways of applying multi-task learning against masked AES implementations (via the ASCAD-r, ASCAD-v2, and CHESCTF-2023 datasets) under the assumption that the attacker cannot access masks during training.
- We offer evidence that multi-task learning significantly increases the consistency of convergence and performance of deep neural networks.
- Our work provides a wide range of experiments to understand the benefits of multi-task strategies over the current single-task stateof-the-art.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2023-006.pdf`
