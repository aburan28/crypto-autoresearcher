---
id: KN-LIT-1853
type: literature
title: "Revisiting DKLs Threshold ECDSA:"
authors:
  - "Enhanced OT-based VOLE"
  - "Two-Party Signing"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/976"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/976"
tags: [cryptanalysis, ecdsa, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Threshold ECDSA signing has become a standard building block for securing cryptocurrency assets, with the protocol of Doerner, Kondi, Lee, and shelat (DKLs, IEEE S&P 2024) emerging as a leading solution due to its efficiency and widespread industry adoption. In this work, we revisit the DKLs protocol to evaluate its concrete security and implementation trade-offs: • Vector Oblivious Linear Evaluation (VOLE): We identify subtle issues in the underlying OT-based Vector Oblivious Linear Evaluation (VOLE) sub-protocol, showing that original parameter choices must be adjusted to reach intended security levels.

## Key claims (as reported)
- To address this, we provide a complete analysis of three VOLE variants offering different trade-offs between bandwidth and round complexity. • Two-Party Signing: We introduce an optimized two-party signing protocol that shifts the majority of computation and communication to a message- and key-independent preprocessing phase.
- This results in an exceptionally efficient online phase where each party exchanges only 0.2KB, a roughly 600× reduction in communication compared to the full protocol, without being susceptible to known “pre-signature” attacks.
- Our findings consolidate the security of the protocol while providing significant efficiency improvements for practical deployment and standardization. ∗ The author is also at Bar-Ilan University.
- Research was conducted for Utila.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-976.pdf`
