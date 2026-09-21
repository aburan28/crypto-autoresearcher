---
id: KN-LIT-1005
type: literature
title: "New Time-Memory Trade-Offs for Subset Sum"
authors:
  - "Improving ISD in Theory"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1329"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1329"
tags: [lattice, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose new time-memory trade-offs for the random subset sum problem defined on (a1 , . . . , an , t) over Z2n . Our trade-offs yield significant running time improvements for every fixed memory limit M ≥ 20.091n .

## Key claims (as reported)
- Furthermore, we interpolate to the running times of the fastest known algorithms when memory is not limited.
- Technically, our design introduces a pruning strategy to the construction by Becker-Coron-Joux (BCJ) that allows for an exponentially small success probability.
- We compensate for this reduced probability by multiple randomized executions.
- Our main improvement stems from the clever reuse of parts of the computation in subsequent executions to reduce the time complexity per iteration.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004057 (1).pdf`
- `downloads/14004057.pdf`
- `downloads/2022-1329.pdf`
