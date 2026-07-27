---
id: KN-LIT-1559
type: literature
title: "AuditPay: Anonymous Payments with Controlled Oversight"
authors:
  - "Elkana Tovey"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1118"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1118"
tags: [elliptic-curve, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces AuditPay, a novel mechanism for blockchain mixers that enables controlled oversight through an “auditing budget.” Auditors may monitor up to a budgeted number of addresses per epoch (e.g., an hour or a day), without revealing to users which addresses are monitored. Unlike traditional approaches that require users to voluntarily disclose viewing keys to trusted gatekeepers, AuditPay cryptographically enforces auditing compliance while preserving privacy for non-monitored user addresses and without introducing additional trust assumptions.

## Key claims (as reported)
- At the core of AuditPay ’s design is a selective encryption mechanism coupled with an efficient audit-key encoding scheme, enforced by a lightweight zero-knowledge proof.
- Users encrypt audit-relevant information under an audit key, which permits decryption only if the payment is to (or, alternatively, from) an address selected by the auditor for monitoring.
- We implement AuditPay as an Ethereum-based payment mixer and show through experiments on our prototype that its performance and gas-cost overheads are modest, providing a practical solution for balancing payment oversight with user privacy.
- CCS CONCEPTS • Security and privacy → Privacy-preserving protocols.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1118.pdf`
