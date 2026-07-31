---
id: KN-LIT-6524
type: literature
title: "Security of the Fiat-Shamir Transformation in the Quantum Random-Oracle Model"
authors:
  - "Jelle Don"
  - "Serge Fehr"
  - "Christian Majenz"
  - "Christian Schaffner"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The famous Fiat-Shamir transformation turns any publiccoin three-round interactive proof, i.e., any so-called Σ-protocol, into a non-interactive proof in the random-oracle model. We study this transformation in the setting of a quantum adversary that in particular may query the random oracle in quantum superposition.

## Key claims (as reported)
- Our main result is a generic reduction that transforms any quantum dishonest prover attacking the Fiat-Shamir transformation in the quantum random-oracle model into a similarly successful quantum dishonest prover attacking the underlying Σ-protocol (in the standard model).
- Applied to the standard soundness and proof-of-knowledge definitions, our reduction implies that both these security properties, in both the computational and the statistical variant, are preserved under the FiatShamir transformation even when allowing quantum attacks.
- Our result improves and completes the partial results that have been known so far, but it also proves wrong certain claims made in the literature.
- In the context of post-quantum secure signature schemes, our results imply that for any Σ-protocol that is a proof-of-knowledge against quantum dishonest provers (and that satisfies some additional natural properties), the corresponding Fiat-Shamir signature scheme is secure in the quantum random-oracle model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940247 (1).pdf`
- `downloads/116940247.pdf`
