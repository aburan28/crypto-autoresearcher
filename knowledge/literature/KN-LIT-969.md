---
id: KN-LIT-969
type: literature
title: "Efficient NIZKs and Signatures from Commit-and-Open Protocols in the QROM?"
authors:
  - "Jelle Don"
  - "Serge Fehr"
  - "Christian Majenz"
  - "Christian Schaffner"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/270"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/270"
tags: [hash, lattice, mov-fr, pairing, pqc, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Commit-and-open Σ-protocols are a popular class of protocols for constructing non-interactive zero-knowledge arguments and digital-signature schemes via the Fiat-Shamir transformation. Instantiated with hash-based commitments, the resulting non-interactive schemes enjoy tight online-extractability in the random oracle model.

## Key claims (as reported)
- Online extractability improves the tightness of security proofs for the resulting digital-signature schemes by avoiding lossy rewinding or forking-lemma based extraction.
- In this work, we prove tight online extractability in the quantum random oracle model (QROM), showing that the construction supports postquantum security.
- First, we consider the default case where committing is done by element-wise hashing.
- In a second part, we extend our result to Merkle-tree based commitments.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070133 (1).pdf`
- `downloads/135070133.pdf`
