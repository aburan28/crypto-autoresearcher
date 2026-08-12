---
id: KN-LIT-1399
type: literature
title: "Hydrangea: Optimistic Two-Round Partial Synchrony with Improved Fault Resilience"
authors:
  - "Nibesh Shrestha"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1112"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1112"
tags: [complexity-theory, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Consensus protocols in the partially synchronous setting face a fundamental trade-off: achieving optimal Byzantine fault tolerance requires a good-case latency1 of at least three rounds, while committing in fewer than three rounds generally entails reduced resilience. Even optimistic protocols such as SBFT (DSN’19), FaB (TDSC’06), and Kudzu (DISC’25) achieve an optimistic good-case latency of two rounds under favorable conditions, but only at the cost of reduced fault tolerance.

## Key claims (as reported)
- In this work, we introduce Hydrangea, a partially synchronous state machine replication protocol that combines low latency with improved fault resilience.
- Let f denote the maximum number of tolerated Byzantine faults, c the maximum number of tolerated crash faults, and k ≥ 0 a tunable parameter.
- For a system of n = 3 f + 2c + k + 1 parties, Hydrangea achieves an optimistic good-case latency of two rounds when the total number of faulty parties (Byzantine or crash) is at most p = ⌊ c+k 2 ⌋.
- In more adversarial settings, with up to f Byzantine faults and c crash faults, it guarantees a good-case latency of three rounds.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1112.pdf`
