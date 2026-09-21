---
id: KN-LIT-1868
type: literature
title: "Security of the Fischlin Transform in Quantum Random Oracle Model"
authors:
  - "Christian Majenz"
  - "Jaya Sharma"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/311"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/311"
tags: [pqc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Fischlin transform yields non-interactive zero-knowledge proofs with straight-line extractability in the classical random oracle model. This is done by forcing a prover to generate multiple accepting transcripts through a proof-of-work mechanism.

## Key claims (as reported)
- Whether the Fischlin transform is straight-line extractable against quantum adversaries has remained open due to the difficulty of reasoning about the likelihood of query transcripts in the quantum-accessible random oracle model (QROM), even when using the compressed oracle methodology.
- In this work, we prove that the Fischlin transform remains straight-line extractable in the QROM, via an extractor based on the compressed oracle.
- This establishes the post-quantum security of the Fischlin transform, providing a post-quantum straight-line extractable NIZK alternative to Pass’ transform with smaller proof size.
- Our techniques are built on different combinations of symmetrization, query amplitude and quantum union bound arguments, as well as tail bounds for sums of independent random variables and for martingales.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-311.pdf`
