---
id: KN-LIT-5712
type: literature
title: "Parallel and Concurrent Security of the"
authors:
  - "HB+ Protocols"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Juels and Weis (building on prior work of Hopper and Blum) propose and analyze two shared-key authentication protocols — HB and HB+ — whose extremely low computational cost makes them attractive for low-cost devices such as radio-frequency identification (RFID) tags. Security of these protocols is based on the conjectured hardness of the “learning parity with noise” (LPN) problem: the HB protocol is proven secure against a passive (eavesdropping) adversary, while the HB+ protocol is proven secure against active attacks.

## Key claims (as reported)
- Juels and Weis prove security of these protocols only for the case of sequential executions, and explicitly leave open the question of whether security holds also in the case of parallel or concurrent executions.
- In addition to guaranteeing security against a stronger class of adversaries, a positive answer to this question would allow the HB+ protocol to be parallelized, thereby substantially reducing its round complexity.
- Adapting a recent result by Regev, we answer the aforementioned question in the affirmative and prove security of the HB and HB+ protocols under parallel/concurrent executions.
- We also give what we believe to be substantially simpler security proofs for these protocols which are more complete in that they explicitly address the dependence of the soundness error on the number of iterations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040074 (1).pdf`
- `downloads/40040074 (2).pdf`
- `downloads/40040074 (3).pdf`
- `downloads/40040074.pdf`
