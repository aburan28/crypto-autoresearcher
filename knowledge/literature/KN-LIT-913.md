---
id: KN-LIT-913
type: literature
title: "Proof of Assets in the Diem Blockchain"
authors:
  - "Panagiotis Chatzigiannis"
  - "Konstantinos Chalkias"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/598"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/598"
tags: [hash, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A great challenge for distributed payment systems is their compliance with regulations, such as anti-money laundering, insolvency legislation, countering the financing of terrorism and sanctions laws. After Bitcoin’s MtGox scandal, one of the most needed auditing functionalities for financial solvency and tax reporting purposes is to prove ownership of blockchain reserves, a process known as Proof of Assets (PoA).

## Key claims (as reported)
- This work formalizes the PoA requirements in account-based blockchains, focusing on the unique hierarchical account structure of the Diem blockchain, formerly known as Libra.
- In particular, we take into account some unique features of the Diem infrastructure to consider different PoA modes by exploring time-stamping edge cases, cold wallets, locked assets, spending-ability delegation and account pruning, among the others.
- We also propose practical optimizations to the byte-size of PoA in the presence of light clients who cannot run a full node, including skipping Validator updates, while still maintaining the 66.67% Byzantine fault tolerance (BFT) guarantee.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-598.pdf`
