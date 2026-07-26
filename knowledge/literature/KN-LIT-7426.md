---
id: KN-LIT-7426
type: literature
title: "Updatable Zero-Knowledge Databases"
authors:
  - "Moses Liskov"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Micali, Rabin, and Kilian [9] recently introduced zero-knowledge sets and databases, in which a prover sets up a database by publishing a commitment, and then gives proofs about particular values. While an elegant and useful primitive, zero-knowledge databases do not offer any good way to perform updates.

## Key claims (as reported)
- We explore the issue of updating zero-knowledge databases.
- We define and discuss transparent updates, which (1) allow holders of proofs that are still valid to update their proofs, but (2) otherwise maintain secrecy about the update.
- We give rigorous definitions for transparently updatable zero-knowledge databases, and give a practical construction based on the Chase et al [2] construction, assuming that verifiable random functions exist and that mercurial commitments exist, in the random oracle model.
- We also investigate the idea of updatable commitments, an attempt to make simple commitments transparently updatable.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/172 (1).pdf`
- `downloads/172 (2).pdf`
- `downloads/172 (3).pdf`
- `downloads/172.pdf`
