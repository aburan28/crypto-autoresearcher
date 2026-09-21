---
id: KN-LIT-1767
type: literature
title: "Obscura: Privacy-Preserving Protocol for the Algorand Blockchain Using LSAG Ring Signatures"
authors:
  - "Navid Azimi"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.02077"
  url: "https://arxiv.org/abs/2605.02077"
tags: [elliptic-curve, hash, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
While public blockchains provide transparent and auditable transaction histories, they inherently compromise user privacy. Existing privacy-enhancing protocols, such as those deployed on Ethereum, typically rely on succinct zero-knowledge proofs (zk-SNARKs) to obscure the transaction graph.

## Key claims (as reported)
- However, implementing comparable cryptographic guarantees on high-throughput blockchains like Algorand is challenging due to strict per-call execution budgets and the state contention introduced by global Merkle accumulators.
- This paper presents Obscura, a decentralized, non-custodial privacy protocol tailored for constrained smart contract environments.
- Obscura achieves transaction anonymity using Linkable Spontaneous Anonymous Group (LSAG) signatures over the BN254 elliptic curve, verified entirely on-chain.
- To overcome limitations of the Algorand Virtual Machine (AVM), we introduce a novel state model that leverages Algorand’s Box Storage for O(1) commitment membership checks, eliminating the need for global Merkle accumulators, and a dynamic opcode-budget expansion mechanism via pooled inner application calls.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.02077v1.pdf`
