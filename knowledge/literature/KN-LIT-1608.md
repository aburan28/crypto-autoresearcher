---
id: KN-LIT-1608
type: literature
title: "Cryptographic Collateralized Loan without Smart Contracts"
authors:
  - "Diego Castejon-Molina"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1123"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1123"
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cryptocurrency lending is growing rapidly, and smart-contractbased loans are expected to grow further. However, existing systems are fundamentally limited: they only operate on smart-contractenabled blockchains, and assets from other blockchains can be used only via tokenized representations.

## Key claims (as reported)
- In this work, we propose an oracle-aided cryptographic protocol that implements the logic of collateralized loans without smart contracts, instead only requiring basic transactions from the underlying blockchain and hence, being compatible with limitedscripting blockchains, including Bitcoin.
- For that, we introduce verifiable graph encryption for signatures (VGES), a new cryptographic primitive that, on input a graph modeling the correspondence between transactions for collateral distribution (vertices) and loan repayments (edges), permits to encrypt the signatures on collateral-distribution transactions ensuring: (1) a signature can only be decrypted after completing loan repayments corresponding to a valid path in the graph from the root (graph enforcement); and (2) anyone can verify that encrypted signatures are valid and can be decrypted after doing the required loan repayments according to the graph (verifiability).
- We present two provably secure constructions of VGES and the evaluation of our implementation shows that they offer a tradeoff between the number of required on-chain transactions and off-chain computation, while both remain efficient on commodity hardware.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1123.pdf`
