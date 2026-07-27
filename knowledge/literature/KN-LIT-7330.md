---
id: KN-LIT-7330
type: literature
title: "UC Commitments for Modular Protocol Design and"
authors:
  - "Applications to Revocation"
  - "Attribute Tokens"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Complex cryptographic protocols are often designed from simple cryptographic primitives, such as signature schemes, encryption schemes, verifiable random functions, and zero-knowledge proofs, by bridging between them with commitments to some of their inputs and outputs. Unfortunately, the known universally composable (UC) functionalities for commitments and the cryptographic primitives mentioned above do not allow such constructions of higher-level protocols as hybrid protocols.

## Key claims (as reported)
- Therefore, protocol designers typically resort to primitives with property-based definitions, often resulting in complex monolithic security proofs that are prone to mistakes and hard to verify.
- We address this gap by presenting a UC functionality for non-interactive commitments that enables modular constructions of complex protocols within the UC framework.
- We also show how the new functionality can be used to construct hybrid protocols that combine different UC functionalities and use commitments to ensure that the same inputs are provided to different functionalities.
- We further provide UC functionalities for attribute tokens and revocation that can be used as building blocks together with our UC commitments.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160202 (1).pdf`
- `downloads/98160202.pdf`
