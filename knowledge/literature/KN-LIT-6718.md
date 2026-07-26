---
id: KN-LIT-6718
type: literature
title: "SNACKs: Leveraging Proofs of Sequential Work for Blockchain Light Clients"
authors:
  - "Hamza Abusalah"
  - "Georg Fuchsbauer"
  - "Peter Gaži"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The success of blockchains has led to ever-growing ledgers that are stored by all participating full nodes. In contrast, light clients only store small amounts of blockchain-related data and rely on the mediation of full nodes when interacting with the ledger.

## Key claims (as reported)
- A broader adoption of blockchains calls for protocols that make this interaction trustless.
- We revisit the design of light-client blockchain protocols from the perspective of classical proof-system theory, and explain the role that proofs of sequential work (PoSWs) can play in it.
- To this end, we define a new primitive called succinct non-interactive argument of chain knowledge (SNACK), a non-interactive proof system that provides clear security guarantees to a verifier (a light client) even when interacting only with a single dishonest prover (a full node).
- We show how augmenting any blockchain with any graph-labeling PoSW (GL-PoSW) enables SNACK proofs for this blockchain.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910160 (1).pdf`
- `downloads/137910160.pdf`
