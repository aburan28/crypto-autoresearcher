---
id: KN-LIT-1734
type: literature
title: "Minimizing Mempool Dependency in PoW Mining on Blockchain: A Paradigm Shift with Compressed Block Representation for"
authors:
  - "Enhanced Scalability"
  - "Decentralization and"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/141"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/141"
tags: [mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
While existing Proof-of-Work (PoW) based blockchain protocols have demonstrated significant utility, they face structural constraints regarding scalability, efficiency, and decentralization. The compact block propagation method, though effective in reducing network bandwidth and propagation delay in synchronized network conditions, suffers from performance degradation due to mempool inconsistencies among nodes.

## Key claims (as reported)
- This paper proposes an asynchronous block propagation and consensus protocol that mitigates the blockchain's dependency on mempool synchronization.
- The proposed approach decouples mining initiation from full validation to optimize throughput despite increased block sizes.
- Specifically, it includes a compressed transaction input ID list within the compact block to enable nodes to immediately initiate mining prior to full verification.
- The full verification of transactions adopts a 'delayed verification' method, performed in parallel with the mining operation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-141.pdf`
