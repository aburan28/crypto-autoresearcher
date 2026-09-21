---
id: KN-LIT-6667
type: literature
title: "Simple, Fast, Efficient, and Tightly-Secure Non-Malleable Non-Interactive Timed Commitments?"
authors:
  - "Peter Chvojka"
  - "Tibor Jager"
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
Timed commitment schemes, introduced by Boneh and Naor (CRYPTO 2000), can be used to achieve fairness in secure computation protocols in a simple and elegant way. The only known non-malleable construction in the standard model is due to Katz, Loss, and Xu (TCC 2020).

## Key claims (as reported)
- This construction requires general-purpose zero knowledge proofs with specific properties, and it suffers from an inefficient commitment protocol, which requires the committing party to solve a computationally expensive puzzle.
- We propose new constructions of non-malleable non-interactive timed commitments, which combine (an extension of) the Naor-Yung paradigm used to construct IND-CCA secure encryption with a non-interactive ZK proof for a simple algebraic language.
- This yields much simpler and more efficient non-malleable timed commitments in the standard model.
- Furthermore, our constructions also compare favourably to known constructions of timed commitments in the random oracle model, as they achieve several further interesting properties that make the schemes very practical.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940037 (1).pdf`
- `downloads/13940037.pdf`
